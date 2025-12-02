const db = require('../config/database');

class SearchHistory {
  static async add(userId, searchQuery, filters = {}, resultsCount = 0) {
    const query = `
      INSERT INTO search_history (user_id, search_query, filters, results_count)
      VALUES ($1, $2, $3, $4)
      RETURNING *
    `;
    const result = await db.query(query, [userId, searchQuery, JSON.stringify(filters), resultsCount]);
    return result.rows[0];
  }

  static async getByUserId(userId, limit = 20) {
    const query = `
      SELECT * FROM search_history
      WHERE user_id = $1
      ORDER BY created_at DESC
      LIMIT $2
    `;
    const result = await db.query(query, [userId, limit]);
    return result.rows;
  }

  static async clearHistory(userId) {
    const query = 'DELETE FROM search_history WHERE user_id = $1';
    await db.query(query, [userId]);
  }

  static async getPopularSearches(limit = 10) {
    const query = `
      SELECT search_query, COUNT(*) as search_count
      FROM search_history
      WHERE created_at > NOW() - INTERVAL '30 days'
      GROUP BY search_query
      ORDER BY search_count DESC
      LIMIT $1
    `;
    const result = await db.query(query, [limit]);
    return result.rows;
  }

  static async getSuggestionsFromHistory(userId, partialQuery, limit = 5) {
    const query = `
      SELECT DISTINCT search_query
      FROM search_history
      WHERE user_id = $1 AND search_query ILIKE $2
      ORDER BY created_at DESC
      LIMIT $3
    `;
    const result = await db.query(query, [userId, `${partialQuery}%`, limit]);
    return result.rows.map(row => row.search_query);
  }
}

module.exports = SearchHistory;
