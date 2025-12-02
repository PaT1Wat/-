const db = require('../config/database');

class Favorite {
  static async add(userId, bookId, listName = 'favorites') {
    const query = `
      INSERT INTO favorites (user_id, book_id, list_name)
      VALUES ($1, $2, $3)
      ON CONFLICT (user_id, book_id, list_name) DO NOTHING
      RETURNING *
    `;
    const result = await db.query(query, [userId, bookId, listName]);
    return result.rows[0];
  }

  static async remove(userId, bookId, listName = null) {
    let query = 'DELETE FROM favorites WHERE user_id = $1 AND book_id = $2';
    const values = [userId, bookId];
    
    if (listName) {
      query += ' AND list_name = $3';
      values.push(listName);
    }
    
    query += ' RETURNING *';
    const result = await db.query(query, values);
    return result.rows[0];
  }

  static async getByUserId(userId, listName = null, page = 1, limit = 20) {
    const offset = (page - 1) * limit;
    let whereClause = 'WHERE f.user_id = $1';
    const values = [userId];
    let paramIndex = 2;

    if (listName) {
      whereClause += ` AND f.list_name = $${paramIndex}`;
      values.push(listName);
      paramIndex++;
    }

    const query = `
      SELECT f.*, 
             b.title, b.title_th, b.cover_image_url, b.type, b.status,
             b.average_rating, b.author_id,
             a.name as author_name, a.name_th as author_name_th
      FROM favorites f
      JOIN books b ON f.book_id = b.id
      LEFT JOIN authors a ON b.author_id = a.id
      ${whereClause}
      ORDER BY f.created_at DESC
      LIMIT $${paramIndex} OFFSET $${paramIndex + 1}
    `;
    values.push(limit, offset);

    const countQuery = `
      SELECT COUNT(*) FROM favorites f ${whereClause}
    `;

    const [result, countResult] = await Promise.all([
      db.query(query, values),
      db.query(countQuery, values.slice(0, listName ? 2 : 1))
    ]);

    return {
      favorites: result.rows,
      total: parseInt(countResult.rows[0].count),
      page,
      totalPages: Math.ceil(countResult.rows[0].count / limit)
    };
  }

  static async checkFavorite(userId, bookId) {
    const query = `
      SELECT list_name FROM favorites 
      WHERE user_id = $1 AND book_id = $2
    `;
    const result = await db.query(query, [userId, bookId]);
    return result.rows;
  }

  static async updateList(userId, bookId, oldListName, newListName) {
    const query = `
      UPDATE favorites 
      SET list_name = $1
      WHERE user_id = $2 AND book_id = $3 AND list_name = $4
      RETURNING *
    `;
    const result = await db.query(query, [newListName, userId, bookId, oldListName]);
    return result.rows[0];
  }

  static async getListCounts(userId) {
    const query = `
      SELECT list_name, COUNT(*) as count
      FROM favorites
      WHERE user_id = $1
      GROUP BY list_name
    `;
    const result = await db.query(query, [userId]);
    return result.rows;
  }
}

module.exports = Favorite;
