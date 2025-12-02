const db = require('../config/database');

class User {
  static async create(userData) {
    const { firebase_uid, email, username, display_name, avatar_url, role = 'user', preferred_language = 'th' } = userData;
    const query = `
      INSERT INTO users (firebase_uid, email, username, display_name, avatar_url, role, preferred_language)
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING *
    `;
    const values = [firebase_uid, email, username, display_name, avatar_url, role, preferred_language];
    const result = await db.query(query, values);
    return result.rows[0];
  }

  static async findById(id) {
    const query = 'SELECT * FROM users WHERE id = $1';
    const result = await db.query(query, [id]);
    return result.rows[0];
  }

  static async findByFirebaseUid(firebase_uid) {
    const query = 'SELECT * FROM users WHERE firebase_uid = $1';
    const result = await db.query(query, [firebase_uid]);
    return result.rows[0];
  }

  static async findByEmail(email) {
    const query = 'SELECT * FROM users WHERE email = $1';
    const result = await db.query(query, [email]);
    return result.rows[0];
  }

  static async findByUsername(username) {
    const query = 'SELECT * FROM users WHERE username = $1';
    const result = await db.query(query, [username]);
    return result.rows[0];
  }

  static async update(id, userData) {
    const { display_name, avatar_url, preferred_language } = userData;
    const query = `
      UPDATE users 
      SET display_name = COALESCE($1, display_name),
          avatar_url = COALESCE($2, avatar_url),
          preferred_language = COALESCE($3, preferred_language)
      WHERE id = $4
      RETURNING *
    `;
    const values = [display_name, avatar_url, preferred_language, id];
    const result = await db.query(query, values);
    return result.rows[0];
  }

  static async updateRole(id, role) {
    const query = 'UPDATE users SET role = $1 WHERE id = $2 RETURNING *';
    const result = await db.query(query, [role, id]);
    return result.rows[0];
  }

  static async delete(id) {
    const query = 'DELETE FROM users WHERE id = $1 RETURNING *';
    const result = await db.query(query, [id]);
    return result.rows[0];
  }

  static async getAll(page = 1, limit = 20) {
    const offset = (page - 1) * limit;
    const query = `
      SELECT id, email, username, display_name, avatar_url, role, created_at
      FROM users 
      ORDER BY created_at DESC 
      LIMIT $1 OFFSET $2
    `;
    const countQuery = 'SELECT COUNT(*) FROM users';
    const [result, countResult] = await Promise.all([
      db.query(query, [limit, offset]),
      db.query(countQuery)
    ]);
    return {
      users: result.rows,
      total: parseInt(countResult.rows[0].count),
      page,
      totalPages: Math.ceil(countResult.rows[0].count / limit)
    };
  }
}

module.exports = User;
