import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import './Header.css';

const Header = () => {
  const { t, i18n } = useTranslation();
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const toggleLanguage = () => {
    const newLang = i18n.language === 'th' ? 'en' : 'th';
    i18n.changeLanguage(newLang);
  };

  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="logo">
          <span className="logo-icon">📚</span>
          <span className="logo-text">MangaRec</span>
        </Link>

        <nav className="nav-links">
          <Link to="/" className="nav-link">{t('nav.home')}</Link>
          <Link to="/search" className="nav-link">{t('nav.search')}</Link>
          {isAuthenticated && (
            <Link to="/favorites" className="nav-link">{t('nav.favorites')}</Link>
          )}
          {isAdmin && (
            <Link to="/admin" className="nav-link">{t('nav.admin')}</Link>
          )}
        </nav>

        <div className="header-actions">
          <button onClick={toggleLanguage} className="lang-btn">
            {i18n.language === 'th' ? '🇹🇭 ไทย' : '🇬🇧 EN'}
          </button>

          {isAuthenticated ? (
            <div className="user-menu">
              <span className="user-name">{user?.display_name || user?.username}</span>
              <button onClick={handleLogout} className="logout-btn">
                {t('nav.logout')}
              </button>
            </div>
          ) : (
            <Link to="/login" className="login-btn">{t('nav.login')}</Link>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
