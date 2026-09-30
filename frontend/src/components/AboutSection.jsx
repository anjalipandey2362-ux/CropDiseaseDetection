import React from 'react';
import { ShieldCheck, Cpu, AlertTriangle, Leaf, Award } from 'lucide-react';
import { translations } from '../utils/translations';
import './AboutSection.css';

export default function AboutSection({ lang = 'en' }) {
  const t = translations[lang] || translations.en;

  return (
    <section className="about-section">
      <div className="container">
        
        {/* Header */}
        <div className="section-header">
          <span className="section-badge">
            <Leaf size={16} />
            <span>{lang === 'hi' ? 'उत्तर प्रदेश कृषि सुरक्षा' : 'Mission & Architecture'}</span>
          </span>
          <h2 className="section-title">
            {lang === 'hi' ? 'प्लांटकेयर एआई के बारे में' : 'About PlantCare AI'}
          </h2>
          <p className="section-subtitle">
            {lang === 'hi'
              ? 'उत्तर प्रदेश के किसानों के लिए समर्पित एआई फसल रोग निदान व सत्यापित उपचार मंच।'
              : 'Dedicated agricultural crop disease detection platform focused on Uttar Pradesh crops & ICAR verified treatment guidelines.'}
          </p>
        </div>

        <div className="about-grid">

          {/* Main Description */}
          <div className="about-card intro-card">
            <h3 className="about-card-title">
              {lang === 'hi' ? 'यूपी कृषि फसल रोग निदान' : 'Uttar Pradesh Crop Diagnostics'}
            </h3>
            <p className="about-text">
              <strong>PlantCare AI</strong> uses EfficientNet-B0 transfer learning and verified Indian agricultural extension databases (ICAR, CSAUA&T Kanpur, UP Department of Agriculture) to provide accurate crop disease identification, low confidence protection, verified active ingredients, and cultural prevention steps for farmers across all 75 districts of Uttar Pradesh.
            </p>
          </div>

          {/* Technology Stack & Model Architecture */}
          <div className="about-card tech-card">
            <div className="card-icon-header">
              <Cpu className="about-icon tech" size={24} />
              <h4>{lang === 'hi' ? 'एआई तकनीक व आर्किटेक्चर' : 'Technology Architecture'}</h4>
            </div>
            <ul className="about-bullets">
              <li><strong>Frontend:</strong> React 18, Vite, Bilingual UI (English | हिंदी)</li>
              <li><strong>Backend API:</strong> Express.js REST Proxy with file & size validation</li>
              <li><strong>ML Engine:</strong> Python FastAPI + PyTorch EfficientNet-B0 transfer learning</li>
              <li><strong>Verified Knowledge Base:</strong> ICAR, UP Agriculture Dept, CSAUA&T Kanpur</li>
              <li><strong>Priority Crops:</strong> Wheat, Paddy/Rice, Sugarcane, Potato, Mustard, Maize, Gram, Arhar, Lentil, Pea</li>
            </ul>
          </div>

          {/* Low Confidence & Safety */}
          <div className="about-card limits-card">
            <div className="card-icon-header">
              <AlertTriangle className="about-icon limits" size={24} />
              <h4>{lang === 'hi' ? 'विश्वसनीयता व सुरक्षा गार्ड' : 'Low Confidence & Safety Guard'}</h4>
            </div>
            <ul className="about-bullets">
              <li>Confidence threshold check (70%): Low confidence predictions hide unverified chemical pesticide names to protect crops.</li>
              <li>No fabricated medicine names: Pesticide and fungicide recommendations come exclusively from verified extension sources.</li>
              <li>Mandatory product label safety note displayed with every chemical treatment.</li>
            </ul>
          </div>

          {/* Responsible Use */}
          <div className="about-card responsible-card">
            <div className="card-icon-header">
              <ShieldCheck className="about-icon responsible" size={24} />
              <h4>{lang === 'hi' ? 'ज़िम्मेदार कृषि उपयोग' : 'Responsible Agricultural Use'}</h4>
            </div>
            <p className="about-text">
              PlantCare AI advocates integrated pest management (IPM), proper crop rotation, sanitation, and biological fungicides (e.g., Trichoderma viride) as first-line measures. Always follow registered product label guidance.
            </p>
          </div>

        </div>

        {/* Important Disclaimer Banner */}
        <div className="about-disclaimer-banner">
          <AlertTriangle size={24} className="disclaimer-alert-svg" />
          <div>
            <h4>Important Disclaimer</h4>
            <p>
              PlantCare AI provides AI-assisted decision support and is not a substitute for professional agricultural diagnosis. Image-based predictions should be verified with local agricultural extension officers when severe symptoms occur.
            </p>
          </div>
        </div>

      </div>
    </section>
  );
}
