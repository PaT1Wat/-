const db = require('../config/database');

class Author {
  static async create(authorData) {
    const { name, name_th, biography, biography_th, avatar_url } = authorData;
    const query = `
      INSERT INTO authors (name, name_th, biography, biography_th, avatar_url)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING *
    `;
    const values = [name, name_th, biography, biography_th, avatar_url];
    const result = await db.query(query, values);
    return result.rows[0];
  }

  static async findById(id) {
    const query = `
      SELECT a.*, 
             (SELECT COUNT(*) FROM books WHERE author_id = a.id) as book_count
      FROM authors a
      WHERE a.id = $1
    `;
    const result = await db.query(query, [id]);
    return result.rows[0];
  }

  static async update(id, authorData) {
    const { name, name_th, biography, biography_th, avatar_url } = authorData;
    const query = `
      UPDATE authors 
      SET name = COALESCE($1, name),
          name_th = COALESCE($2, name_th),
          biography = COALESCE($3, biography),
          biography_th = COALESCE($4, biography_th),
          avatar_url = COALESCE($5, avatar_url)
      WHERE id = $6
      RETURNING *
    `;
    const values = [name, name_th, biography, biography_th, avatar_url, id];
    const result = await db.query(query, values);
    return result.rows[0];
  }

  static async delete(id) {
    const query = 'DELETE FROM authors WHERE id = $1 RETURNING *';
    const result = await db.query(query, [id]);
    return result.rows[0];
  }

  static async getAll(page = 1, limit = 20) {
    const offset = (page - 1) * limit;
    const query = `
      SELECT a.*, 
             (SELECT COUNT(*) FROM books WHERE author_id = a.id) as book_count
      FROM authors a
      ORDER BY a.name ASC
      LIMIT $1 OFFSET $2
    `;
    const countQuery = 'SELECT COUNT(*) FROM authors';
    const [result, countResult] = await Promise.all([
      db.query(query, [limit, offset]),
      db.query(countQuery)
    ]);
    return {
      authors: result.rows,
      total: parseInt(countResult.rows[0].count),
      page,
      totalPages: Math.ceil(countResult.rows[0].count / limit)
    };
  }

  static async search(searchQuery, limit = 10) {
    const query = `
      SELECT a.*, 
             (SELECT COUNT(*) FROM books WHERE author_id = a.id) as book_count
      FROM authors a
      WHERE a.name ILIKE $1 OR a.name_th ILIKE $1
      ORDER BY a.name ASC
      LIMIT $2
    `;
    const result = await db.query(query, [`%${searchQuery}%`, limit]);
    return result.rows;
  }

  static async getBooks(authorId, page = 1, limit = 20) {
    const offset = (page - 1) * limit;
    const query = `
      SELECT b.*
      FROM books b
      WHERE b.author_id = $1
      ORDER BY b.created_at DESC
      LIMIT $2 OFFSET $3
    `;
    const result = await db.query(query, [authorId, limit, offset]);
    return result.rows;
  }
}

module.exports = Author;
