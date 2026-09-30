import React, { useState, useEffect } from 'react';
import { History, Trash2, Calendar, ArrowRight, ShieldCheck, AlertCircle, MapPin } from 'lucide-react';
import { translations } from '../utils/translations';
import './HistorySection.css';

export default function HistorySection({ onSelectHistoryItem, lang = 'en' }) {
  const [historyItems, setHistoryItems] = useState([]);
  const t = translations[lang] || translations.en;

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = () => {
    try {
      const stored = localStorage.getItem('plantcare_history');
      if (stored) {
        setHistoryItems(JSON.parse(stored));
      }
    } catch (e) {
      console.error("Failed to read history from localStorage:", e);
    }
  };

  const handleClearHistory = () => {
    const confirmMsg = lang === 'hi' 
      ? 'क्या आप वास्तव में अपना इतिहास साफ करना चाहते हैं?' 
      : 'Are you sure you want to clear your local analysis history?';

    if (window.confirm(confirmMsg)) {
      localStorage.removeItem('plantcare_history');
      setHistoryItems([]);
    }
  };

  return (
    <section className="history-section">
      <div className="container">

        <div className="section-header">
          <span className="section-badge">
            <History size={16} />
            <span>{lang === 'hi' ? 'ब्राउज़र स्टोरेज' : 'Browser Storage'}</span>
          </span>
          <h2 className="section-title">{t.historyTitle}</h2>
          <p className="section-subtitle">
            {lang === 'hi'
              ? 'आपके द्वारा पूर्व में जांची गई फसल पत्तियों का परिणाम और रिपोर्ट।'
              : 'Review your previously analyzed crop foliage diagnoses.'}
          </p>
        </div>

        {/* Informational Privacy Note */}
        <div className="history-privacy-banner">
          <ShieldCheck size={18} className="privacy-icon" />
          <p>
            <strong>Privacy Note:</strong> Local history is stored safely inside your browser (localStorage). No photos or records are transmitted to external cloud databases.
          </p>
        </div>

        {/* History List or Empty state */}
        {historyItems.length > 0 ? (
          <div className="history-content-wrapper">
            <div className="history-list-header">
              <span className="count-label">{historyItems.length} {lang === 'hi' ? 'जांच रिकॉर्ड सुरक्षित' : 'past records saved'}</span>
              <button className="btn-clear-history" onClick={handleClearHistory}>
                <Trash2 size={16} />
                <span>{t.clearHistory}</span>
              </button>
            </div>

            <div className="history-grid">
              {historyItems.map((item, idx) => (
                <div key={idx} className="history-card animate-fade-in" onClick={() => onSelectHistoryItem(item)}>
                  {item.thumbnail ? (
                    <div className="history-thumb-box">
                      <img src={item.thumbnail} alt={item.crop || item.plant} className="history-thumb" />
                    </div>
                  ) : (
                    <div className="history-thumb-box placeholder">🌾</div>
                  )}

                  <div className="history-card-body">
                    <div className="history-card-top">
                      <span className="history-plant">🌾 {item.crop || item.plant}</span>
                      <span className="history-conf">{(item.confidence * 100).toFixed(0)}% Conf.</span>
                    </div>

                    <h4 className="history-disease">{item.disease}</h4>

                    <div className="history-card-footer">
                      <span className="history-date">
                        <Calendar size={13} />
                        <span>{item.date ? new Date(item.date).toLocaleDateString() : 'Recent'}</span>
                      </span>

                      {item.district && (
                        <span className="history-date" style={{ color: '#047857' }}>
                          <MapPin size={13} />
                          <span>{item.district}</span>
                        </span>
                      )}

                      <button className="btn-view-record">
                        <span>View</span>
                        <ArrowRight size={14} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="history-empty-box">
            <AlertCircle size={36} className="empty-icon" />
            <h3>{lang === 'hi' ? 'कोई पुराना इतिहास नहीं मिला' : 'No Analysis History Found'}</h3>
            <p>{lang === 'hi' ? 'आपके द्वारा की गई नई जांचों का रिकॉर्ड यहाँ स्वतः दिखाई देगा।' : 'Diagnoses you perform will automatically appear here for quick reference during your browser session.'}</p>
          </div>
        )}

      </div>
    </section>
  );
}

/**
 * Helper function to save a result to localStorage
 */
export function saveResultToHistory(resultData, imageUrl) {
  try {
    const existing = JSON.parse(localStorage.getItem('plantcare_history') || '[]');
    const newRecord = {
      id: Date.now(),
      date: new Date().toISOString(),
      crop: resultData.crop || resultData.plant,
      disease: resultData.disease,
      confidence: resultData.confidence,
      severity: resultData.severity,
      symptoms: resultData.symptoms,
      verifiedTreatment: resultData.verifiedTreatment,
      culturalManagement: resultData.culturalManagement,
      prevention: resultData.prevention,
      district: resultData.district || 'Lucknow',
      thumbnail: imageUrl || null
    };

    // Keep max 25 recent items to conserve storage space
    const updated = [newRecord, ...existing].slice(0, 25);
    localStorage.setItem('plantcare_history', JSON.stringify(updated));
  } catch (e) {
    console.error("Could not save to history:", e);
  }
}
