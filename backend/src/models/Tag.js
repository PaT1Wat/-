const db = require('../config/database');

class Tag {
  static async create(tagData) {
    const { name, name_th, category = 'genre' } = tagData;
    const query = `
      INSERT INTO tags (name, name_th, category)
      VALUES ($1, $2, $3)
      RETURNING *
    `;
    const result = await db.query(query, [name, name_th, category]);
    return result.rows[0];
  }

  static async findById(id) {
    const query = 'SELECT * FROM tags WHERE id = $1';
    const result = await db.query(query, [id]);
    return result.rows[0];
  }

  static async findByName(name) {
    const query = 'SELECT * FROM tags WHERE name = $1 OR name_th = $1';
    const result = await db.query(query, [name]);
    return result.rows[0];
  }

  static async update(id, tagData) {
    const { name, name_th, category } = tagData;
    const query = `
      UPDATE tags 
      SET name = COALESCE($1, name),
          name_th = COALESCE($2, name_th),
          category = COALESCE($3, category)
      WHERE id = $4
      RETURNING *
    `;
    const result = await db.query(query, [name, name_th, category, id]);
    return result.rows[0];
  }

  static async delete(id) {
    const query = 'DELETE FROM tags WHERE id = $1 RETURNING *';
    const result = await db.query(query, [id]);
    return result.rows[0];
  }

  static async getAll(category = null) {
    let query = 'SELECT * FROM tags';
    const values = [];
    
    if (category) {
      query += ' WHERE category = $1';
      values.push(category);
    }
    
    query += ' ORDER BY category, name';
    const result = await db.query(query, values);
    return result.rows;
  }

  static async search(searchQuery, limit = 10) {
    const query = `
      SELECT * FROM tags
      WHERE name ILIKE $1 OR name_th ILIKE $1
      ORDER BY name
      LIMIT $2
    `;
    const result = await db.query(query, [`%${searchQuery}%`, limit]);
    return result.rows;
  }

  static async getPopular(limit = 20) {
    const query = `
      SELECT t.*, COUNT(bt.book_id) as book_count
      FROM tags t
      LEFT JOIN book_tags bt ON t.id = bt.tag_id
      GROUP BY t.id
      ORDER BY book_count DESC
      LIMIT $1
    `;
    const result = await db.query(query, [limit]);
    return result.rows;
  }

  static async getByCategory(category) {
    const query = 'SELECT * FROM tags WHERE category = $1 ORDER BY name';
    const result = await db.query(query, [category]);
    return result.rows;
  }
}

module.exports = Tag;
