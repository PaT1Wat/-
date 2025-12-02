const db = require('../config/database');

class Review {
  static async create(reviewData) {
    const { user_id, book_id, rating, title, content, is_spoiler = false } = reviewData;
    const query = `
      INSERT INTO reviews (user_id, book_id, rating, title, content, is_spoiler)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING *
    `;
    const values = [user_id, book_id, rating, title, content, is_spoiler];
    const result = await db.query(query, values);
    return result.rows[0];
  }

  static async findById(id) {
    const query = `
      SELECT r.*, 
             u.username, u.display_name, u.avatar_url as user_avatar,
             b.title as book_title, b.title_th as book_title_th
      FROM reviews r
      JOIN users u ON r.user_id = u.id
      JOIN books b ON r.book_id = b.id
      WHERE r.id = $1
    `;
    const result = await db.query(query, [id]);
    return result.rows[0];
  }

  static async update(id, userId, reviewData) {
    const { rating, title, content, is_spoiler } = reviewData;
    const query = `
      UPDATE reviews 
      SET rating = COALESCE($1, rating),
          title = COALESCE($2, title),
          content = COALESCE($3, content),
          is_spoiler = COALESCE($4, is_spoiler)
      WHERE id = $5 AND user_id = $6
      RETURNING *
    `;
    const values = [rating, title, content, is_spoiler, id, userId];
    const result = await db.query(query, values);
    return result.rows[0];
  }

  static async delete(id, userId = null) {
    let query = 'DELETE FROM reviews WHERE id = $1';
    const values = [id];
    
    if (userId) {
      query += ' AND user_id = $2';
      values.push(userId);
    }
    
    query += ' RETURNING *';
    const result = await db.query(query, values);
    return result.rows[0];
  }

  static async getByBookId(bookId, page = 1, limit = 10, sortBy = 'created_at') {
    const offset = (page - 1) * limit;
    const validSortFields = ['created_at', 'rating', 'helpful_count'];
    const sortField = validSortFields.includes(sortBy) ? sortBy : 'created_at';
    
    const query = `
      SELECT r.*, 
             u.username, u.display_name, u.avatar_url as user_avatar
      FROM reviews r
      JOIN users u ON r.user_id = u.id
      WHERE r.book_id = $1 AND r.is_approved = true
      ORDER BY r.${sortField} DESC
      LIMIT $2 OFFSET $3
    `;
    const countQuery = 'SELECT COUNT(*) FROM reviews WHERE book_id = $1 AND is_approved = true';
    
    const [result, countResult] = await Promise.all([
      db.query(query, [bookId, limit, offset]),
      db.query(countQuery, [bookId])
    ]);

    return {
      reviews: result.rows,
      total: parseInt(countResult.rows[0].count),
      page,
      totalPages: Math.ceil(countResult.rows[0].count / limit)
    };
  }

  static async getByUserId(userId, page = 1, limit = 10) {
    const offset = (page - 1) * limit;
    const query = `
      SELECT r.*, 
             b.title as book_title, b.title_th as book_title_th, b.cover_image_url
      FROM reviews r
      JOIN books b ON r.book_id = b.id
      WHERE r.user_id = $1
      ORDER BY r.created_at DESC
      LIMIT $2 OFFSET $3
    `;
    const countQuery = 'SELECT COUNT(*) FROM reviews WHERE user_id = $1';
    
    const [result, countResult] = await Promise.all([
      db.query(query, [userId, limit, offset]),
      db.query(countQuery, [userId])
    ]);

    return {
      reviews: result.rows,
      total: parseInt(countResult.rows[0].count),
      page,
      totalPages: Math.ceil(countResult.rows[0].count / limit)
    };
  }

  static async findByUserAndBook(userId, bookId) {
    const query = 'SELECT * FROM reviews WHERE user_id = $1 AND book_id = $2';
    const result = await db.query(query, [userId, bookId]);
    return result.rows[0];
  }

  static async incrementHelpful(id) {
    const query = 'UPDATE reviews SET helpful_count = helpful_count + 1 WHERE id = $1 RETURNING *';
    const result = await db.query(query, [id]);
    return result.rows[0];
  }

  static async getPendingReviews(page = 1, limit = 20) {
    const offset = (page - 1) * limit;
    const query = `
      SELECT r.*, 
             u.username, u.display_name,
             b.title as book_title
      FROM reviews r
      JOIN users u ON r.user_id = u.id
      JOIN books b ON r.book_id = b.id
      WHERE r.is_approved = false
      ORDER BY r.created_at DESC
      LIMIT $1 OFFSET $2
    `;
    const countQuery = 'SELECT COUNT(*) FROM reviews WHERE is_approved = false';
    
    const [result, countResult] = await Promise.all([
      db.query(query, [limit, offset]),
      db.query(countQuery)
    ]);

    return {
      reviews: result.rows,
      total: parseInt(countResult.rows[0].count),
      page,
      totalPages: Math.ceil(countResult.rows[0].count / limit)
    };
  }

  static async approve(id) {
    const query = 'UPDATE reviews SET is_approved = true WHERE id = $1 RETURNING *';
    const result = await db.query(query, [id]);
    return result.rows[0];
  }

  static async reject(id) {
    const query = 'DELETE FROM reviews WHERE id = $1 RETURNING *';
    const result = await db.query(query, [id]);
    return result.rows[0];
  }
}

module.exports = Review;
