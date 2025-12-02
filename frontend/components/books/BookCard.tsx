'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useI18n } from '@/contexts/I18nContext';
import type { Book } from '@/lib/types';

interface BookCardProps {
  book: Book;
  showRating?: boolean;
}

export default function BookCard({ book, showRating = true }: BookCardProps) {
  const { t, language } = useI18n();
  const title = language === 'th' && book.title_th ? book.title_th : book.title;
  const authorName = language === 'th' && book.author_name_th ? book.author_name_th : book.author_name;

  const typeColors: Record<string, string> = {
    manga: 'bg-pink-600',
    novel: 'bg-purple-600',
    light_novel: 'bg-violet-700',
    manhwa: 'bg-blue-700',
    manhua: 'bg-blue-500'
  };

  const statusColors: Record<string, string> = {
    ongoing: 'bg-blue-100 text-blue-700',
    completed: 'bg-green-100 text-green-700',
    hiatus: 'bg-orange-100 text-orange-700',
    cancelled: 'bg-red-100 text-red-700'
  };

  return (
    <Link 
      href={`/book/${book.id}`} 
      className="bg-white rounded-xl overflow-hidden shadow-md hover:shadow-xl hover:-translate-y-1 transition-all flex flex-col no-underline text-inherit"
    >
      <div className="relative aspect-[2/3] overflow-hidden bg-gray-100">
        {book.cover_image_url ? (
          <Image 
            src={book.cover_image_url} 
            alt={title}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 50vw, 20vw"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-200 to-gray-100">
            <span className="text-5xl opacity-50">📖</span>
          </div>
        )}
        {book.type && (
          <span className={`absolute top-2 right-2 ${typeColors[book.type] || 'bg-gray-600'} text-white px-2 py-1 rounded text-xs font-semibold uppercase`}>
            {t(`type.${book.type}` as keyof typeof t)}
          </span>
        )}
      </div>
      
      <div className="p-3 flex-1 flex flex-col gap-1">
        <h3 className="font-semibold text-gray-800 line-clamp-2 text-sm m-0">{title}</h3>
        {authorName && (
          <p className="text-xs text-gray-600 m-0">{authorName}</p>
        )}
        {showRating && book.average_rating && Number(book.average_rating) > 0 && (
          <div className="flex items-center gap-1 mt-auto">
            <span className="text-base">⭐</span>
            <span className="font-semibold text-amber-500">{Number(book.average_rating).toFixed(1)}</span>
            <span className="text-xs text-gray-400">({book.total_reviews || 0})</span>
          </div>
        )}
        {book.status && (
          <span className={`text-xs px-2 py-0.5 rounded self-start ${statusColors[book.status] || 'bg-gray-100 text-gray-600'}`}>
            {t(`status.${book.status}` as keyof typeof t)}
          </span>
        )}
      </div>
    </Link>
  );
}
