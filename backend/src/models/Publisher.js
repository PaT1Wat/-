const db = require('../config/database');

class Publisher {
  static async create(publisherData) {
    const { name, name_th, description, description_th, website_url, logo_url } = publisherData;
    const query = `
      INSERT INTO publishers (name, name_th, description, description_th, website_url, logo_url)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING *
    `;
    const values = [name, name_th, description, description_th, website_url, logo_url];
    const result = await db.query(query, values);
    return result.rows[0];
  }

  static async findById(id) {
    const query = `
      SELECT p.*, 
             (SELECT COUNT(*) FROM books WHERE publisher_id = p.id) as book_count
      FROM publishers p
      WHERE p.id = $1
    `;
    const result = await db.query(query, [id]);
    return result.rows[0];
  }

  static async update(id, publisherData) {
    const { name, name_th, description, description_th, website_url, logo_url } = publisherData;
    const query = `
      UPDATE publishers 
      SET name = COALESCE($1, name),
          name_th = COALESCE($2, name_th),
          description = COALESCE($3, description),
          description_th = COALESCE($4, description_th),
          website_url = COALESCE($5, website_url),
          logo_url = COALESCE($6, logo_url)
      WHERE id = $7
      RETURNING *
    `;
    const values = [name, name_th, description, description_th, website_url, logo_url, id];
    const result = await db.query(query, values);
    return result.rows[0];
  }

  static async delete(id) {
    const query = 'DELETE FROM publishers WHERE id = $1 RETURNING *';
    const result = await db.query(query, [id]);
    return result.rows[0];
  }

  static async getAll(page = 1, limit = 20) {
    const offset = (page - 1) * limit;
    const query = `
      SELECT p.*, 
             (SELECT COUNT(*) FROM books WHERE publisher_id = p.id) as book_count
      FROM publishers p
      ORDER BY p.name ASC
      LIMIT $1 OFFSET $2
    `;
    const countQuery = 'SELECT COUNT(*) FROM publishers';
    const [result, countResult] = await Promise.all([
      db.query(query, [limit, offset]),
      db.query(countQuery)
    ]);
    return {
      publishers: result.rows,
      total: parseInt(countResult.rows[0].count),
      page,
      totalPages: Math.ceil(countResult.rows[0].count / limit)
    };
  }

  static async search(searchQuery, limit = 10) {
    const query = `
      SELECT p.*, 
             (SELECT COUNT(*) FROM books WHERE publisher_id = p.id) as book_count
      FROM publishers p
      WHERE p.name ILIKE $1 OR p.name_th ILIKE $1
      ORDER BY p.name ASC
      LIMIT $2
    `;
    const result = await db.query(query, [`%${searchQuery}%`, limit]);
    return result.rows;
  }

  static async getBooks(publisherId, page = 1, limit = 20) {
    const offset = (page - 1) * limit;
    const query = `
      SELECT b.*
      FROM books b
      WHERE b.publisher_id = $1
      ORDER BY b.created_at DESC
      LIMIT $2 OFFSET $3
    `;
    const result = await db.query(query, [publisherId, limit, offset]);
    return result.rows;
  }
}

module.exports = Publisher;
