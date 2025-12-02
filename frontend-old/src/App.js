import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import './i18n';
import './App.css';

// Layout
import Header from './components/layout/Header';

// Pages
import Home from './pages/Home';
import Search from './pages/Search';
import BookDetail from './pages/BookDetail';
import Login from './pages/Login';
import Favorites from './pages/Favorites';
import Admin from './pages/Admin';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Header />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/search" element={<Search />} />
              <Route path="/book/:id" element={<BookDetail />} />
              <Route path="/login" element={<Login />} />
              <Route path="/favorites" element={<Favorites />} />
              <Route path="/admin" element={<Admin />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
