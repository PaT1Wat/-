'use client';

import Link from 'next/link';
import { useI18n } from '@/contexts/I18nContext';
import BookCard from './BookCard';
import type { Book } from '@/lib/types';

interface BookGridProps {
  title?: string;
  books: Book[];
  loading?: boolean;
  viewAllLink?: string;
  emptyMessage?: string;
}

export default function BookGrid({ title, books, loading, viewAllLink, emptyMessage }: BookGridProps) {
  const { t } = useI18n();

  if (loading) {
    return (
      <div className="mb-8">
        {title && <h2 className="text-2xl font-bold mb-4">{title}</h2>}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="aspect-[2/3] bg-gray-200 rounded-xl mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!books || books.length === 0) {
    return (
      <div className="mb-8">
        {title && <h2 className="text-2xl font-bold mb-4">{title}</h2>}
        <p className="text-gray-500 text-center py-8">{emptyMessage || t('search.noResults')}</p>
      </div>
    );
  }

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        {title && <h2 className="text-2xl font-bold">{title}</h2>}
        {viewAllLink && (
          <Link href={viewAllLink} className="text-indigo-600 hover:text-indigo-800 font-medium">
            {t('common.viewAll')} →
          </Link>
        )}
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {books.map((book) => (
          <BookCard key={book.id} book={book} />
        ))}
      </div>
    </div>
  );
}
