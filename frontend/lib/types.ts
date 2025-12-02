// Book type definitions
export interface Tag {
  id: string;
  name: string;
  name_th?: string;
  category?: string;
}

export interface Book {
  id: string;
  title: string;
  title_th?: string;
  original_title?: string;
  description?: string;
  description_th?: string;
  cover_image_url?: string;
  type?: 'manga' | 'novel' | 'light_novel' | 'manhwa' | 'manhua';
  status?: 'ongoing' | 'completed' | 'hiatus' | 'cancelled';
  publication_year?: number;
  total_chapters?: number;
  total_volumes?: number;
  author_id?: string;
  publisher_id?: string;
  average_rating?: number;
  total_ratings?: number;
  total_reviews?: number;
  view_count?: number;
  author_name?: string;
  author_name_th?: string;
  publisher_name?: string;
  publisher_name_th?: string;
  tags?: Tag[];
  created_at?: string;
  updated_at?: string;
}

export interface Author {
  id: string;
  name: string;
  name_th?: string;
  biography?: string;
  biography_th?: string;
  avatar_url?: string;
  book_count?: number;
  created_at?: string;
  updated_at?: string;
}

export interface Publisher {
  id: string;
  name: string;
  name_th?: string;
  description?: string;
  description_th?: string;
  website_url?: string;
  logo_url?: string;
  book_count?: number;
  created_at?: string;
  updated_at?: string;
}

export interface Review {
  id: string;
  user_id: string;
  book_id: string;
  rating: number;
  title?: string;
  content?: string;
  is_spoiler?: boolean;
  is_approved?: boolean;
  helpful_count?: number;
  username?: string;
  display_name?: string;
  user_avatar?: string;
  book_title?: string;
  book_title_th?: string;
  cover_image_url?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Favorite {
  id: string;
  user_id: string;
  book_id: string;
  list_name: string;
  title?: string;
  title_th?: string;
  cover_image_url?: string;
  type?: string;
  status?: string;
  average_rating?: number;
  author_id?: string;
  author_name?: string;
  author_name_th?: string;
  created_at?: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  display_name?: string;
  avatar_url?: string;
  role: 'user' | 'admin' | 'moderator';
  preferred_language?: string;
  created_at?: string;
}

export interface Pagination {
  page: number;
  totalPages: number;
  total: number;
}
