import React from 'react';
import { Sparkles, ArrowRight, ShieldCheck, Leaf, Activity } from 'lucide-react';
import { translations } from '../utils/translations';
import './Hero.css';

export default function Hero({ onAnalyzeClick, onHowItWorksClick, lang = 'en' }) {
  const t = translations[lang] || translations.en;

  return (
    <section className="hero-section">
      <div className="container hero-container">
        
        {/* Left Text Column */}
        <div className="hero-content">
          <div className="badge-wrapper">
            <span className="hero-badge">
              <Sparkles className="badge-icon" size={16} />
              <span>{t.heroBadge}</span>
            </span>
          </div>

          <h1 className="hero-heading">
            {lang === 'hi' ? (
              <>उत्तर प्रदेश <span className="text-gradient">फसल रोग</span> पहचान एवं उपचार</>
            ) : (
              <>AI-Powered <span className="text-gradient">Crop Disease</span> Detection for Uttar Pradesh</>
            )}
          </h1>

          <p className="hero-subheading">
            {t.heroSub}
          </p>

          {/* Action CTA Buttons */}
          <div className="hero-actions">
            <button className="btn-hero-primary" onClick={onAnalyzeClick}>
              <span>{t.analyzeBtn}</span>
              <ArrowRight size={18} />
            </button>

            <button className="btn-hero-secondary" onClick={onHowItWorksClick}>
              <span>{lang === 'hi' ? 'यह कैसे काम करता है' : 'How It Works'}</span>
            </button>
          </div>

          {/* Important Informational Note */}
          <div className="hero-disclaimer-note">
            <ShieldCheck className="disclaimer-icon" size={18} />
            <p>
              {lang === 'hi' 
                ? 'रासायनिक दवाओं का प्रयोग केवल सत्यापित कृषि गाइडलाइन व उत्पाद लेबल के अनुसार ही करें।' 
                : 'Pesticide recommendations are strictly sourced from verified agricultural extension databases.'}
            </p>
          </div>

          {/* Quick Stats Banner */}
          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-number">10+</span>
              <span className="stat-label">{t.heroStatCrops}</span>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <span className="stat-number">75</span>
              <span className="stat-label">{t.heroStatDistricts}</span>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <span className="stat-number">EfficientNet</span>
              <span className="stat-label">{t.heroStatAccuracy}</span>
            </div>
          </div>
        </div>

        {/* Right Visual Graphic */}
        <div className="hero-visual">
          <div className="hero-card-glow"></div>
          
          <div className="hero-image-card">
            {/* Visual Header Badge */}
            <div className="card-status-badge">
              <Activity className="status-icon" size={16} />
              <span>{lang === 'hi' ? 'कंप्यूटर विज़न एआई' : 'Realtime Computer Vision'}</span>
            </div>

            {/* Main Visual Image SVG/Graphic */}
            <div className="leaf-visual-wrapper">
              <div className="leaf-graphic">
                <Leaf size={100} className="floating-leaf-icon" />
                <div className="scanning-line"></div>
                
                {/* Detection Pins overlay */}
                <div className="detection-pin pin-1">
                  <span className="pin-dot"></span>
                  <span className="pin-text">Yellow Rust 94%</span>
                </div>
                <div className="detection-pin pin-2">
                  <span className="pin-dot"></span>
                  <span className="pin-text">Wheat / गेहूं</span>
                </div>
              </div>
            </div>

            {/* Quick Result Mock Preview */}
            <div className="hero-preview-result">
              <div className="result-preview-icon">🌾</div>
              <div className="result-preview-info">
                <h4>{lang === 'hi' ? 'गेहूं (Wheat)' : 'Wheat Crop'}</h4>
                <p>{lang === 'hi' ? 'पीला रस्ट पहचान (94% विश्वसनीयता)' : 'Stripe / Yellow Rust (94% Conf.)'}</p>
              </div>
              <span className="preview-badge severe">{lang === 'hi' ? 'उच्च' : 'High'}</span>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
}
