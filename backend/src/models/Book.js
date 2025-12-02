const db = require('../config/database');

class Book {
  static async create(bookData) {
    const {
      title, title_th, original_title, description, description_th,
      cover_image_url, type = 'manga', status = 'ongoing',
      publication_year, total_chapters, total_volumes, author_id, publisher_id
    } = bookData;
    
    const query = `
      INSERT INTO books (
        title, title_th, original_title, description, description_th,
        cover_image_url, type, status, publication_year, total_chapters,
        total_volumes, author_id, publisher_id
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
      RETURNING *
    `;
    const values = [
      title, title_th, original_title, description, description_th,
      cover_image_url, type, status, publication_year, total_chapters,
      total_volumes, author_id, publisher_id
    ];
    const result = await db.query(query, values);
    return result.rows[0];
  }

  static async findById(id) {
    const query = `
      SELECT b.*, 
             a.name as author_name, a.name_th as author_name_th,
             p.name as publisher_name, p.name_th as publisher_name_th,
             COALESCE(
               (SELECT json_agg(json_build_object('id', t.id, 'name', t.name, 'name_th', t.name_th, 'category', t.category))
                FROM book_tags bt JOIN tags t ON bt.tag_id = t.id WHERE bt.book_id = b.id),
               '[]'
             ) as tags
      FROM books b
      LEFT JOIN authors a ON b.author_id = a.id
      LEFT JOIN publishers p ON b.publisher_id = p.id
      WHERE b.id = $1
    `;
    const result = await db.query(query, [id]);
    return result.rows[0];
  }

  static async update(id, bookData) {
    const fields = [];
    const values = [];
    let paramIndex = 1;

    const allowedFields = [
      'title', 'title_th', 'original_title', 'description', 'description_th',
      'cover_image_url', 'type', 'status', 'publication_year', 'total_chapters',
      'total_volumes', 'author_id', 'publisher_id'
    ];

    for (const field of allowedFields) {
      if (bookData[field] !== undefined) {
        fields.push(`${field} = $${paramIndex}`);
        values.push(bookData[field]);
        paramIndex++;
      }
    }

    if (fields.length === 0) {
      return this.findById(id);
    }

    values.push(id);
    const query = `
      UPDATE books SET ${fields.join(', ')}
      WHERE id = $${paramIndex}
      RETURNING *
    `;
    const result = await db.query(query, values);
    return result.rows[0];
  }

  static async delete(id) {
    const query = 'DELETE FROM books WHERE id = $1 RETURNING *';
    const result = await db.query(query, [id]);
    return result.rows[0];
  }

  static async search(searchParams) {
    const {
      query: searchQuery, type, status, tags, author_id, publisher_id,
      min_rating, year_from, year_to, sort_by = 'average_rating',
      sort_order = 'DESC', page = 1, limit = 20
    } = searchParams;

    const conditions = [];
    const values = [];
    let paramIndex = 1;

    // Full-text search on title and description (supports Thai)
    if (searchQuery) {
      conditions.push(`(
        b.title ILIKE $${paramIndex} OR 
        b.title_th ILIKE $${paramIndex} OR 
        b.original_title ILIKE $${paramIndex} OR
        b.description ILIKE $${paramIndex} OR
        b.description_th ILIKE $${paramIndex}
      )`);
      values.push(`%${searchQuery}%`);
      paramIndex++;
    }

    if (type) {
      conditions.push(`b.type = $${paramIndex}`);
      values.push(type);
      paramIndex++;
    }

    if (status) {
      conditions.push(`b.status = $${paramIndex}`);
      values.push(status);
      paramIndex++;
    }

    if (author_id) {
      conditions.push(`b.author_id = $${paramIndex}`);
      values.push(author_id);
      paramIndex++;
    }

    if (publisher_id) {
      conditions.push(`b.publisher_id = $${paramIndex}`);
      values.push(publisher_id);
      paramIndex++;
    }

    if (min_rating) {
      conditions.push(`b.average_rating >= $${paramIndex}`);
      values.push(min_rating);
      paramIndex++;
    }

    if (year_from) {
      conditions.push(`b.publication_year >= $${paramIndex}`);
      values.push(year_from);
      paramIndex++;
    }

    if (year_to) {
      conditions.push(`b.publication_year <= $${paramIndex}`);
      values.push(year_to);
      paramIndex++;
    }

    // Tag filtering
    if (tags && tags.length > 0) {
      conditions.push(`
        b.id IN (
          SELECT bt.book_id FROM book_tags bt 
          JOIN tags t ON bt.tag_id = t.id 
          WHERE t.name = ANY($${paramIndex})
        )
      `);
      values.push(tags);
      paramIndex++;
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';
    const offset = (page - 1) * limit;

    // Validate sort_by to prevent SQL injection
    const validSortFields = ['average_rating', 'created_at', 'title', 'publication_year', 'view_count', 'total_reviews'];
    const sortField = validSortFields.includes(sort_by) ? sort_by : 'average_rating';
    const sortDir = sort_order.toUpperCase() === 'ASC' ? 'ASC' : 'DESC';

    const query = `
      SELECT b.*, 
             a.name as author_name, a.name_th as author_name_th,
             p.name as publisher_name, p.name_th as publisher_name_th,
             COALESCE(
               (SELECT json_agg(json_build_object('id', t.id, 'name', t.name, 'name_th', t.name_th))
                FROM book_tags bt JOIN tags t ON bt.tag_id = t.id WHERE bt.book_id = b.id),
               '[]'
             ) as tags
      FROM books b
      LEFT JOIN authors a ON b.author_id = a.id
      LEFT JOIN publishers p ON b.publisher_id = p.id
      ${whereClause}
      ORDER BY b.${sortField} ${sortDir}
      LIMIT $${paramIndex} OFFSET $${paramIndex + 1}
    `;
    values.push(limit, offset);

    const countQuery = `
      SELECT COUNT(*) FROM books b ${whereClause}
    `;

    const [result, countResult] = await Promise.all([
      db.query(query, values),
      db.query(countQuery, values.slice(0, -2))
    ]);

    return {
      books: result.rows,
      total: parseInt(countResult.rows[0].count),
      page,
      totalPages: Math.ceil(countResult.rows[0].count / limit)
    };
  }

  static async autocomplete(searchQuery, limit = 10) {
    const query = `
      SELECT id, title, title_th, cover_image_url, type
      FROM books
      WHERE title ILIKE $1 OR title_th ILIKE $1 OR original_title ILIKE $1
      ORDER BY view_count DESC, average_rating DESC
      LIMIT $2
    `;
    const result = await db.query(query, [`%${searchQuery}%`, limit]);
    return result.rows;
  }

  static async addTags(bookId, tagIds) {
    const values = tagIds.map((tagId, index) => `($1, $${index + 2})`).join(', ');
    const query = `
      INSERT INTO book_tags (book_id, tag_id)
      VALUES ${values}
      ON CONFLICT DO NOTHING
    `;
    await db.query(query, [bookId, ...tagIds]);
  }

  static async removeTags(bookId, tagIds) {
    const query = 'DELETE FROM book_tags WHERE book_id = $1 AND tag_id = ANY($2)';
    await db.query(query, [bookId, tagIds]);
  }

  static async incrementViewCount(id) {
    const query = 'UPDATE books SET view_count = view_count + 1 WHERE id = $1';
    await db.query(query, [id]);
  }

  static async getPopular(limit = 10) {
    const query = `
      SELECT b.*, a.name as author_name, a.name_th as author_name_th
      FROM books b
      LEFT JOIN authors a ON b.author_id = a.id
      ORDER BY b.average_rating DESC, b.total_reviews DESC
      LIMIT $1
    `;
    const result = await db.query(query, [limit]);
    return result.rows;
  }

  static async getRecent(limit = 10) {
    const query = `
      SELECT b.*, a.name as author_name, a.name_th as author_name_th
      FROM books b
      LEFT JOIN authors a ON b.author_id = a.id
      ORDER BY b.created_at DESC
      LIMIT $1
    `;
    const result = await db.query(query, [limit]);
    return result.rows;
  }

  static async getByType(type, limit = 20, page = 1) {
    const offset = (page - 1) * limit;
    const query = `
      SELECT b.*, a.name as author_name, a.name_th as author_name_th
      FROM books b
      LEFT JOIN authors a ON b.author_id = a.id
      WHERE b.type = $1
      ORDER BY b.average_rating DESC
      LIMIT $2 OFFSET $3
    `;
    const result = await db.query(query, [type, limit, offset]);
    return result.rows;
  }
}

module.exports = Book;
