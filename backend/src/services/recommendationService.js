const natural = require('natural');
const db = require('../config/database');

// TF-IDF instance for content-based filtering
const TfIdf = natural.TfIdf;
const tfidf = new TfIdf();

class RecommendationService {
  constructor() {
    this.bookVectors = new Map();
    this.userItemMatrix = new Map();
    this.initialized = false;
  }

  // Initialize TF-IDF vectors for all books
  async initializeTfIdf() {
    try {
      const query = `
        SELECT b.id, b.title, b.title_th, b.description, b.description_th, b.type,
               COALESCE(
                 (SELECT string_agg(t.name, ' ') FROM book_tags bt JOIN tags t ON bt.tag_id = t.id WHERE bt.book_id = b.id),
                 ''
               ) as tags
        FROM books b
      `;
      const result = await db.query(query);
      
      // Reset TF-IDF
      const newTfidf = new TfIdf();
      
      result.rows.forEach((book, index) => {
        // Combine all text features for TF-IDF
        const document = [
          book.title || '',
          book.title_th || '',
          book.description || '',
          book.description_th || '',
          book.type || '',
          book.tags || ''
        ].join(' ').toLowerCase();
        
        newTfidf.addDocument(document);
        this.bookVectors.set(book.id, index);
      });
      
      this.tfidf = newTfidf;
      this.books = result.rows;
      this.initialized = true;
      
      console.log(`TF-IDF initialized with ${result.rows.length} books`);
    } catch (error) {
      console.error('Error initializing TF-IDF:', error);
    }
  }

  // Calculate cosine similarity between two vectors
  cosineSimilarity(vecA, vecB) {
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    
    for (let i = 0; i < vecA.length; i++) {
      dotProduct += vecA[i] * vecB[i];
      normA += vecA[i] * vecA[i];
      normB += vecB[i] * vecB[i];
    }
    
    if (normA === 0 || normB === 0) return 0;
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
  }

  // Get TF-IDF vector for a book
  getTfIdfVector(bookIndex) {
    if (!this.tfidf || bookIndex === undefined) return [];
    
    const vector = [];
    this.tfidf.listTerms(bookIndex).forEach(item => {
      vector.push(item.tfidf);
    });
    return vector;
  }

  // Content-based filtering using TF-IDF + Cosine Similarity
  async getContentBasedRecommendations(bookId, limit = 10) {
    if (!this.initialized) {
      await this.initializeTfIdf();
    }

    const bookIndex = this.bookVectors.get(bookId);
    if (bookIndex === undefined) {
      return [];
    }

    const similarities = [];
    const targetTerms = {};
    
    // Get terms for target book
    this.tfidf.listTerms(bookIndex).forEach(term => {
      targetTerms[term.term] = term.tfidf;
    });

    // Calculate similarity with all other books
    this.books.forEach((book, index) => {
      if (book.id === bookId) return;
      
      let similarity = 0;
      const bookTerms = {};
      
      this.tfidf.listTerms(index).forEach(term => {
        bookTerms[term.term] = term.tfidf;
      });

      // Calculate cosine similarity
      const allTerms = new Set([...Object.keys(targetTerms), ...Object.keys(bookTerms)]);
      let dotProduct = 0;
      let normTarget = 0;
      let normBook = 0;

      allTerms.forEach(term => {
        const targetVal = targetTerms[term] || 0;
        const bookVal = bookTerms[term] || 0;
        dotProduct += targetVal * bookVal;
        normTarget += targetVal * targetVal;
        normBook += bookVal * bookVal;
      });

      if (normTarget > 0 && normBook > 0) {
        similarity = dotProduct / (Math.sqrt(normTarget) * Math.sqrt(normBook));
      }

      if (similarity > 0) {
        similarities.push({ bookId: book.id, similarity });
      }
    });

    // Sort by similarity and return top N
    similarities.sort((a, b) => b.similarity - a.similarity);
    return similarities.slice(0, limit);
  }

  // Build user-item interaction matrix for collaborative filtering
  async buildUserItemMatrix() {
    const query = `
      SELECT 
        user_id,
        book_id,
        COALESCE(
          (SELECT rating FROM reviews WHERE user_id = ui.user_id AND book_id = ui.book_id),
          3
        ) + SUM(interaction_weight) as score
      FROM user_interactions ui
      GROUP BY user_id, book_id
      UNION
      SELECT user_id, book_id, rating as score
      FROM reviews
    `;
    const result = await db.query(query);
    
    this.userItemMatrix.clear();
    const userIds = new Set();
    const bookIds = new Set();
    
    result.rows.forEach(row => {
      userIds.add(row.user_id);
      bookIds.add(row.book_id);
      
      if (!this.userItemMatrix.has(row.user_id)) {
        this.userItemMatrix.set(row.user_id, new Map());
      }
      this.userItemMatrix.get(row.user_id).set(row.book_id, parseFloat(row.score));
    });
    
    this.userIds = Array.from(userIds);
    this.bookIds = Array.from(bookIds);
  }

  // KNN-based collaborative filtering
  async getKNNRecommendations(userId, k = 5, limit = 10) {
    await this.buildUserItemMatrix();
    
    if (!this.userItemMatrix.has(userId)) {
      return [];
    }

    const targetUserRatings = this.userItemMatrix.get(userId);
    const similarities = [];

    // Find K nearest neighbors
    this.userIds.forEach(otherUserId => {
      if (otherUserId === userId) return;
      
      const otherUserRatings = this.userItemMatrix.get(otherUserId);
      if (!otherUserRatings) return;

      // Calculate similarity based on common items
      const commonBooks = [];
      targetUserRatings.forEach((rating, bookId) => {
        if (otherUserRatings.has(bookId)) {
          commonBooks.push({
            targetRating: rating,
            otherRating: otherUserRatings.get(bookId)
          });
        }
      });

      if (commonBooks.length < 2) return;

      // Pearson correlation
      const n = commonBooks.length;
      const sumTarget = commonBooks.reduce((sum, item) => sum + item.targetRating, 0);
      const sumOther = commonBooks.reduce((sum, item) => sum + item.otherRating, 0);
      const sumTargetSq = commonBooks.reduce((sum, item) => sum + item.targetRating * item.targetRating, 0);
      const sumOtherSq = commonBooks.reduce((sum, item) => sum + item.otherRating * item.otherRating, 0);
      const sumProduct = commonBooks.reduce((sum, item) => sum + item.targetRating * item.otherRating, 0);

      const numerator = n * sumProduct - sumTarget * sumOther;
      const denominator = Math.sqrt((n * sumTargetSq - sumTarget * sumTarget) * (n * sumOtherSq - sumOther * sumOther));

      if (denominator > 0) {
        const similarity = numerator / denominator;
        if (similarity > 0) {
          similarities.push({ userId: otherUserId, similarity });
        }
      }
    });

    // Get top K neighbors
    similarities.sort((a, b) => b.similarity - a.similarity);
    const neighbors = similarities.slice(0, k);

    if (neighbors.length === 0) {
      return [];
    }

    // Predict ratings for unseen books
    const predictions = new Map();
    const targetBooks = new Set(targetUserRatings.keys());

    neighbors.forEach(neighbor => {
      const neighborRatings = this.userItemMatrix.get(neighbor.userId);
      neighborRatings.forEach((rating, bookId) => {
        if (!targetBooks.has(bookId)) {
          if (!predictions.has(bookId)) {
            predictions.set(bookId, { weightedSum: 0, similaritySum: 0 });
          }
          const pred = predictions.get(bookId);
          pred.weightedSum += rating * neighbor.similarity;
          pred.similaritySum += neighbor.similarity;
        }
      });
    });

    // Calculate final predictions
    const recommendations = [];
    predictions.forEach((pred, bookId) => {
      if (pred.similaritySum > 0) {
        recommendations.push({
          bookId,
          predictedRating: pred.weightedSum / pred.similaritySum
        });
      }
    });

    // Sort by predicted rating
    recommendations.sort((a, b) => b.predictedRating - a.predictedRating);
    return recommendations.slice(0, limit);
  }

  // Simple SVD-inspired matrix factorization
  async getSVDRecommendations(userId, factors = 10, limit = 10) {
    await this.buildUserItemMatrix();
    
    if (!this.userItemMatrix.has(userId) || this.userIds.length < 2) {
      return [];
    }

    // Build rating matrix
    const matrix = [];
    const userIndex = new Map();
    const bookIndex = new Map();
    
    this.userIds.forEach((uid, i) => userIndex.set(uid, i));
    this.bookIds.forEach((bid, i) => bookIndex.set(bid, i));

    // Initialize matrix with zeros
    for (let i = 0; i < this.userIds.length; i++) {
      matrix.push(new Array(this.bookIds.length).fill(0));
    }

    // Fill in known ratings
    this.userItemMatrix.forEach((ratings, uid) => {
      const uIdx = userIndex.get(uid);
      ratings.forEach((rating, bookId) => {
        const bIdx = bookIndex.get(bookId);
        if (bIdx !== undefined) {
          matrix[uIdx][bIdx] = rating;
        }
      });
    });

    // Simple gradient descent for matrix factorization
    const numUsers = this.userIds.length;
    const numBooks = this.bookIds.length;
    const learningRate = 0.01;
    const regularization = 0.02;
    const iterations = 100;

    // Initialize factor matrices with small random values
    const userFactors = [];
    const bookFactors = [];
    
    for (let i = 0; i < numUsers; i++) {
      userFactors.push(Array.from({ length: factors }, () => Math.random() * 0.1));
    }
    for (let i = 0; i < numBooks; i++) {
      bookFactors.push(Array.from({ length: factors }, () => Math.random() * 0.1));
    }

    // Training
    for (let iter = 0; iter < iterations; iter++) {
      for (let u = 0; u < numUsers; u++) {
        for (let b = 0; b < numBooks; b++) {
          if (matrix[u][b] > 0) {
            // Calculate prediction
            let prediction = 0;
            for (let f = 0; f < factors; f++) {
              prediction += userFactors[u][f] * bookFactors[b][f];
            }
            
            // Calculate error
            const error = matrix[u][b] - prediction;
            
            // Update factors
            for (let f = 0; f < factors; f++) {
              const userFactor = userFactors[u][f];
              const bookFactor = bookFactors[b][f];
              userFactors[u][f] += learningRate * (error * bookFactor - regularization * userFactor);
              bookFactors[b][f] += learningRate * (error * userFactor - regularization * bookFactor);
            }
          }
        }
      }
    }

    // Generate predictions for target user
    const targetUserIdx = userIndex.get(userId);
    const targetUserRatings = this.userItemMatrix.get(userId);
    const recommendations = [];

    this.bookIds.forEach((bookId, bIdx) => {
      if (!targetUserRatings.has(bookId)) {
        let prediction = 0;
        for (let f = 0; f < factors; f++) {
          prediction += userFactors[targetUserIdx][f] * bookFactors[bIdx][f];
        }
        recommendations.push({ bookId, predictedRating: prediction });
      }
    });

    recommendations.sort((a, b) => b.predictedRating - a.predictedRating);
    return recommendations.slice(0, limit);
  }

  // Hybrid recommendation combining content-based and collaborative filtering
  async getHybridRecommendations(userId, bookId = null, limit = 10) {
    const recommendations = new Map();
    const weights = {
      contentBased: 0.3,
      knn: 0.4,
      svd: 0.3
    };

    try {
      // Get content-based recommendations if book is provided
      if (bookId) {
        const contentRecs = await this.getContentBasedRecommendations(bookId, limit * 2);
        contentRecs.forEach(rec => {
          recommendations.set(rec.bookId, {
            bookId: rec.bookId,
            score: (recommendations.get(rec.bookId)?.score || 0) + rec.similarity * weights.contentBased
          });
        });
      }

      // Get KNN-based recommendations
      const knnRecs = await this.getKNNRecommendations(userId, 5, limit * 2);
      knnRecs.forEach(rec => {
        recommendations.set(rec.bookId, {
          bookId: rec.bookId,
          score: (recommendations.get(rec.bookId)?.score || 0) + (rec.predictedRating / 5) * weights.knn
        });
      });

      // Get SVD-based recommendations
      const svdRecs = await this.getSVDRecommendations(userId, 10, limit * 2);
      svdRecs.forEach(rec => {
        recommendations.set(rec.bookId, {
          bookId: rec.bookId,
          score: (recommendations.get(rec.bookId)?.score || 0) + (rec.predictedRating / 5) * weights.svd
        });
      });
    } catch (error) {
      console.error('Error in hybrid recommendations:', error);
    }

    // Sort by combined score
    const sortedRecs = Array.from(recommendations.values())
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);

    // Fetch book details
    if (sortedRecs.length > 0) {
      const bookIds = sortedRecs.map(r => r.bookId);
      const query = `
        SELECT b.*, a.name as author_name, a.name_th as author_name_th
        FROM books b
        LEFT JOIN authors a ON b.author_id = a.id
        WHERE b.id = ANY($1)
      `;
      const result = await db.query(query, [bookIds]);
      
      const bookMap = new Map(result.rows.map(book => [book.id, book]));
      return sortedRecs.map(rec => ({
        ...bookMap.get(rec.bookId),
        recommendationScore: rec.score
      })).filter(book => book.id);
    }

    return [];
  }

  // Get personalized recommendations based on user behavior
  async getPersonalizedRecommendations(userId, limit = 10) {
    // Get user's preferences
    const preferencesQuery = `
      SELECT 
        t.id, t.name, t.category,
        SUM(ui.interaction_weight) as preference_score
      FROM user_interactions ui
      JOIN book_tags bt ON ui.book_id = bt.book_id
      JOIN tags t ON bt.tag_id = t.id
      WHERE ui.user_id = $1
      GROUP BY t.id, t.name, t.category
      ORDER BY preference_score DESC
      LIMIT 5
    `;
    const prefResult = await db.query(preferencesQuery, [userId]);
    
    if (prefResult.rows.length === 0) {
      // Return popular books for new users
      return this.getPopularBooks(limit);
    }

    const preferredTags = prefResult.rows.map(r => r.id);
    
    // Get books user hasn't interacted with but match preferences
    const query = `
      SELECT DISTINCT b.*, a.name as author_name, a.name_th as author_name_th,
             COUNT(bt.tag_id) as matching_tags
      FROM books b
      LEFT JOIN authors a ON b.author_id = a.id
      JOIN book_tags bt ON b.id = bt.book_id
      WHERE bt.tag_id = ANY($1)
        AND b.id NOT IN (
          SELECT book_id FROM user_interactions WHERE user_id = $2
          UNION
          SELECT book_id FROM reviews WHERE user_id = $2
          UNION
          SELECT book_id FROM favorites WHERE user_id = $2
        )
      GROUP BY b.id, a.name, a.name_th
      ORDER BY matching_tags DESC, b.average_rating DESC
      LIMIT $3
    `;
    
    const result = await db.query(query, [preferredTags, userId, limit]);
    return result.rows;
  }

  // Get popular books for cold start
  async getPopularBooks(limit = 10) {
    const query = `
      SELECT b.*, a.name as author_name, a.name_th as author_name_th
      FROM books b
      LEFT JOIN authors a ON b.author_id = a.id
      ORDER BY b.average_rating DESC, b.total_reviews DESC, b.view_count DESC
      LIMIT $1
    `;
    const result = await db.query(query, [limit]);
    return result.rows;
  }

  // Get similar books based on tags
  async getSimilarBooksByTags(bookId, limit = 10) {
    const query = `
      WITH book_tags_list AS (
        SELECT tag_id FROM book_tags WHERE book_id = $1
      )
      SELECT b.*, a.name as author_name, a.name_th as author_name_th,
             COUNT(bt.tag_id) as common_tags
      FROM books b
      LEFT JOIN authors a ON b.author_id = a.id
      JOIN book_tags bt ON b.id = bt.book_id
      WHERE bt.tag_id IN (SELECT tag_id FROM book_tags_list)
        AND b.id != $1
      GROUP BY b.id, a.name, a.name_th
      ORDER BY common_tags DESC, b.average_rating DESC
      LIMIT $2
    `;
    const result = await db.query(query, [bookId, limit]);
    return result.rows;
  }
}

// Export singleton instance
module.exports = new RecommendationService();
