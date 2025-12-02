'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { useI18n } from '@/contexts/I18nContext';

export default function Header() {
  const { t, language, toggleLanguage } = useI18n();
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push('/');
  };

  return (
    <header className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-3 sticky top-0 z-50 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between flex-wrap gap-4">
        <Link href="/" className="flex items-center gap-2 text-2xl font-bold no-underline text-white">
          <span className="text-3xl">📚</span>
          <span>MangaRec</span>
        </Link>

        <nav className="flex gap-4">
          <Link href="/" className="text-white/90 hover:text-white hover:bg-white/20 px-4 py-2 rounded-lg transition-all">
            {t('nav.home')}
          </Link>
          <Link href="/search" className="text-white/90 hover:text-white hover:bg-white/20 px-4 py-2 rounded-lg transition-all">
            {t('nav.search')}
          </Link>
          {isAuthenticated && (
            <Link href="/favorites" className="text-white/90 hover:text-white hover:bg-white/20 px-4 py-2 rounded-lg transition-all">
              {t('nav.favorites')}
            </Link>
          )}
          {isAdmin && (
            <Link href="/admin" className="text-white/90 hover:text-white hover:bg-white/20 px-4 py-2 rounded-lg transition-all">
              {t('nav.admin')}
            </Link>
          )}
        </nav>

        <div className="flex items-center gap-4">
          <button 
            onClick={toggleLanguage} 
            className="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-lg text-sm transition-all"
          >
            {language === 'th' ? '🇹🇭 ไทย' : '🇬🇧 EN'}
          </button>

          {isAuthenticated ? (
            <div className="flex items-center gap-3">
              <span className="text-sm">{user?.display_name || user?.username}</span>
              <button 
                onClick={handleLogout} 
                className="bg-white text-indigo-600 px-5 py-2 rounded-lg font-medium hover:transform hover:-translate-y-0.5 hover:shadow-lg transition-all"
              >
                {t('nav.logout')}
              </button>
            </div>
          ) : (
            <Link 
              href="/login" 
              className="bg-white text-indigo-600 px-5 py-2 rounded-lg font-medium hover:transform hover:-translate-y-0.5 hover:shadow-lg transition-all no-underline"
            >
              {t('nav.login')}
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
