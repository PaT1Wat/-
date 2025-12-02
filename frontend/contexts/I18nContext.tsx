'use client';

import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { translations, Language, TranslationKey } from '@/lib/i18n';

interface I18nContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: TranslationKey) => string;
  toggleLanguage: () => void;
}

const I18nContext = createContext<I18nContextType | null>(null);

export const useI18n = () => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
};

interface I18nProviderProps {
  children: ReactNode;
  defaultLanguage?: Language;
}

export const I18nProvider = ({ children, defaultLanguage = 'th' }: I18nProviderProps) => {
  const [language, setLanguageState] = useState<Language>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('language') as Language;
      return stored && (stored === 'th' || stored === 'en') ? stored : defaultLanguage;
    }
    return defaultLanguage;
  });

  const setLanguage = useCallback((lang: Language) => {
    setLanguageState(lang);
    if (typeof window !== 'undefined') {
      localStorage.setItem('language', lang);
    }
  }, []);

  const toggleLanguage = useCallback(() => {
    const newLang = language === 'th' ? 'en' : 'th';
    setLanguage(newLang);
  }, [language, setLanguage]);

  const t = useCallback((key: TranslationKey): string => {
    return translations[language][key] || key;
  }, [language]);

  const value: I18nContextType = {
    language,
    setLanguage,
    t,
    toggleLanguage
  };

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
};

export default I18nContext;
