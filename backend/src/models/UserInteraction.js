const db = require('../config/database');

class UserInteraction {
  static async record(userId, bookId, interactionType, weight = 1.0) {
    const query = `
      INSERT INTO user_interactions (user_id, book_id, interaction_type, interaction_weight)
      VALUES ($1, $2, $3, $4)
      RETURNING *
    `;
    const result = await db.query(query, [userId, bookId, interactionType, weight]);
    return result.rows[0];
  }

  static async getByUserId(userId, limit = 100) {
    const query = `
      SELECT ui.*, b.title, b.title_th, b.type
      FROM user_interactions ui
      JOIN books b ON ui.book_id = b.id
      WHERE ui.user_id = $1
      ORDER BY ui.created_at DESC
      LIMIT $2
    `;
    const result = await db.query(query, [userId, limit]);
    return result.rows;
  }

  static async getInteractionMatrix() {
    // Get user-book interaction matrix for collaborative filtering
    const query = `
      SELECT 
        user_id,
        book_id,
        SUM(interaction_weight) as total_weight
      FROM user_interactions
      GROUP BY user_id, book_id
    `;
    const result = await db.query(query);
    return result.rows;
  }

  static async getUserPreferences(userId) {
    // Get aggregated user preferences based on interactions
    const query = `
      SELECT 
        t.id as tag_id,
        t.name as tag_name,
        t.category,
        SUM(ui.interaction_weight) as preference_score
      FROM user_interactions ui
      JOIN book_tags bt ON ui.book_id = bt.book_id
      JOIN tags t ON bt.tag_id = t.id
      WHERE ui.user_id = $1
      GROUP BY t.id, t.name, t.category
      ORDER BY preference_score DESC
    `;
    const result = await db.query(query, [userId]);
    return result.rows;
  }

  static async getSimilarUsers(userId, limit = 10) {
    // Find users with similar interaction patterns
    const query = `
      WITH user_books AS (
        SELECT DISTINCT book_id FROM user_interactions WHERE user_id = $1
      )
      SELECT 
        ui.user_id,
        COUNT(DISTINCT ui.book_id) as common_books
      FROM user_interactions ui
      JOIN user_books ub ON ui.book_id = ub.book_id
      WHERE ui.user_id != $1
      GROUP BY ui.user_id
      ORDER BY common_books DESC
      LIMIT $2
    `;
    const result = await db.query(query, [userId, limit]);
    return result.rows;
  }
}

module.exports = UserInteraction;
