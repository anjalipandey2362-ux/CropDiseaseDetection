import React, { useState, useEffect } from 'react';
import { Leaf, Menu, X, Sparkles, Languages } from 'lucide-react';
import { translations } from '../utils/translations';
import './Navbar.css';

export default function Navbar({ activePage, setActivePage, onNavigateToDetect, lang = 'en', onToggleLang }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  const t = translations[lang] || translations.en;

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navItems = [
    { id: 'home', label: t.navHome },
    { id: 'detect', label: t.navDetect },
    { id: 'diseases', label: t.navLibrary },
    { id: 'weather', label: t.navWeather },
    { id: 'history', label: t.navHistory },
    { id: 'about', label: t.navAbout },
  ];

  const handleNavClick = (id) => {
    setActivePage(id);
    setMobileMenuOpen(false);
    if (id === 'detect' && onNavigateToDetect) {
      onNavigateToDetect();
    }
  };

  return (
    <header className={`navbar-header ${scrolled ? 'scrolled' : ''}`}>
      <div className="container navbar-container">
        {/* Brand Logo */}
        <div className="navbar-brand" onClick={() => handleNavClick('home')}>
          <div className="brand-icon-wrapper">
            <Leaf className="brand-icon" />
          </div>
          <div className="brand-text">
            <span className="brand-name">
              {t.brandName} <span className="brand-accent">{t.brandAccent}</span>
            </span>
            <span className="brand-tagline">
              {lang === 'hi' ? 'उत्तर प्रदेश कृषि फसल सुरक्षा' : 'Uttar Pradesh Agriculture'}
            </span>
          </div>
        </div>

        {/* Desktop Navigation */}
        <nav className="desktop-nav">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-link ${activePage === item.id ? 'active' : ''}`}
              onClick={() => handleNavClick(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>

        {/* Action Buttons & Language Switcher */}
        <div className="navbar-action">
          {/* Language Switcher Button */}
          <button 
            className="btn-lang-toggle" 
            onClick={onToggleLang}
            title={lang === 'en' ? 'Switch to Hindi (हिंदी)' : 'Switch to English'}
          >
            <Languages size={16} />
            <span>{lang === 'en' ? 'English | हिंदी' : 'हिंदी | English'}</span>
          </button>

          <button className="btn-analyze" onClick={() => handleNavClick('detect')}>
            <Sparkles className="btn-icon" size={16} />
            <span>{t.analyzeBtn}</span>
          </button>

          {/* Mobile Hamburger Toggle */}
          <button 
            className="mobile-toggle" 
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Drawer */}
      {mobileMenuOpen && (
        <div className="mobile-menu animate-fade-in">
          <div className="mobile-menu-links">
            {navItems.map((item) => (
              <button
                key={item.id}
                className={`mobile-nav-link ${activePage === item.id ? 'active' : ''}`}
                onClick={() => handleNavClick(item.id)}
              >
                {item.label}
              </button>
            ))}
            <button 
              className="btn-lang-toggle mobile-lang-btn"
              onClick={onToggleLang}
              style={{ width: '100%', justifyContent: 'center', margin: '6px 0' }}
            >
              <Languages size={16} />
              <span>{lang === 'en' ? 'English | हिंदी' : 'हिंदी | English'}</span>
            </button>
            <button 
              className="btn-analyze mobile-analyze-btn"
              onClick={() => handleNavClick('detect')}
            >
              <Sparkles size={18} />
              <span>{t.analyzeBtn}</span>
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
