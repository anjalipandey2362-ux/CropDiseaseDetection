import React from 'react';
import { Leaf, ShieldCheck, MapPin } from 'lucide-react';
import { translations } from '../utils/translations';
import './Footer.css';

export default function Footer({ onNavigate, lang = 'en' }) {
  const t = translations[lang] || translations.en;

  return (
    <footer className="footer-container">
      <div className="container footer-content">
        
        {/* Brand Column */}
        <div className="footer-brand-col">
          <div className="footer-logo" onClick={() => onNavigate('home')}>
            <div className="footer-icon-bg">
              <Leaf size={20} />
            </div>
            <span className="footer-brand-name">PlantCare <span>AI</span></span>
          </div>
          <p className="footer-tagline">"Uttar Pradesh Agriculture Crop Care"</p>
          <p className="footer-desc">
            {lang === 'hi'
              ? 'उत्तर प्रदेश की प्रमुख फसलों (गेहूं, धान, गन्ना, आलू, सरसों, मक्का, चना) के लिए एआई आधारित रोग निदान व सत्यापित उपचार।'
              : 'AI-powered crop disease detection and verified ICAR treatment guidance for Uttar Pradesh farmers across all 75 districts.'}
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem', color: '#166534', fontWeight: 700, marginTop: '8px' }}>
            <MapPin size={15} />
            <span>Uttar Pradesh, India (75 Districts)</span>
          </div>
        </div>

        {/* Quick Links */}
        <div className="footer-links-col">
          <h4 className="footer-col-title">{lang === 'hi' ? 'नेविगेशन' : 'Quick Navigation'}</h4>
          <ul className="footer-links-list">
            <li><button onClick={() => onNavigate('home')}>{t.navHome}</button></li>
            <li><button onClick={() => onNavigate('detect')}>{t.navDetect}</button></li>
            <li><button onClick={() => onNavigate('diseases')}>{t.navLibrary}</button></li>
            <li><button onClick={() => onNavigate('weather')}>{t.navWeather}</button></li>
            <li><button onClick={() => onNavigate('history')}>{t.navHistory}</button></li>
            <li><button onClick={() => onNavigate('about')}>{t.navAbout}</button></li>
          </ul>
        </div>

        {/* Important Disclaimer Column */}
        <div className="footer-disclaimer-col">
          <h4 className="footer-col-title">Agricultural Notice</h4>
          <p className="footer-disclaimer-text">
            PlantCare AI offers decision support based on automated image recognition and verified agricultural extension data. Always verify recommendations with a local agricultural officer.
          </p>
          <div className="footer-secure-badge">
            <ShieldCheck size={16} />
            <span>Verified Agricultural Database (ICAR / UP Ag Dept)</span>
          </div>
        </div>

      </div>

      <div className="footer-bottom">
        <div className="container footer-bottom-inner">
          <p>© {new Date().getFullYear()} PlantCare AI — Uttar Pradesh Agricultural Platform. All rights reserved.</p>
          <p className="built-with">
            EfficientNet-B0 PyTorch • Express.js • React
          </p>
        </div>
      </div>
    </footer>
  );
}
