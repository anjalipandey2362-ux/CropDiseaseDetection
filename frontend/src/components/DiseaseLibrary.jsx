import React, { useState, useEffect } from 'react';
import { Search, Stethoscope, ShieldCheck, Leaf, Sparkles, BookOpen, Pill } from 'lucide-react';
import { fetchDiseaseLibraryApi, fetchCropsApi } from '../services/plantApi';
import { translations } from '../utils/translations';
import './DiseaseLibrary.css';

export default function DiseaseLibrary({ onSelectCropForDetection, lang = 'en' }) {
  const [diseases, setDiseases] = useState([]);
  const [crops, setCrops] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCropFilter, setSelectedCropFilter] = useState('All');
  const [selectedDiseaseModal, setSelectedDiseaseModal] = useState(null);

  const t = translations[lang] || translations.en;

  useEffect(() => {
    async function loadData() {
      const dData = await fetchDiseaseLibraryApi();
      setDiseases(dData);

      const cData = await fetchCropsApi();
      setCrops(cData);
    }
    loadData();
  }, []);

  const priorityCrops = ['All', 'Wheat', 'Rice / Paddy', 'Sugarcane', 'Potato', 'Maize', 'Mustard', 'Chickpea / Gram', 'Pigeon Pea / Arhar'];

  const filteredDiseases = diseases.filter((item) => {
    const matchesSearch = 
      item.crop.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.disease.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.diseaseHindi && item.diseaseHindi.includes(searchQuery)) ||
      item.symptoms.some(s => s.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesCrop = 
      selectedCropFilter === 'All' || 
      item.crop.toLowerCase().includes(selectedCropFilter.toLowerCase());

    return matchesSearch && matchesCrop;
  });

  return (
    <section className="library-section">
      <div className="container">

        {/* Section Title Header */}
        <div className="section-header">
          <span className="section-badge">
            <Leaf size={16} />
            <span>{lang === 'hi' ? 'उत्तर प्रदेश कृषि ज्ञान कोष' : 'UP Agricultural Disease & Crop Library'}</span>
          </span>
          <h2 className="section-title">
            {lang === 'hi' ? 'उत्तर प्रदेश फसल व रोग पुस्तकालय' : 'Uttar Pradesh Crop & Disease Library'}
          </h2>
          <p className="section-subtitle">
            {lang === 'hi'
              ? 'गेहूं, धान, गन्ना, आलू, सरसों, चना व अरहर सहित उत्तर प्रदेश की प्रमुख फसलों के रोगों, लक्षणों व सत्यापित उपचारों की जानकारी।'
              : 'Explore priority crops of UP (Wheat, Paddy, Sugarcane, Potato, Mustard, Gram), identify disease symptoms, and review verified ICAR treatment guidelines.'}
          </p>
        </div>

        {/* Search & Filter Controls */}
        <div className="library-controls">
          <div className="search-input-wrapper">
            <Search size={18} className="search-icon" />
            <input
              type="text"
              placeholder={lang === 'hi' ? 'फसल (जैसे गेहूं, धान) या रोग के नाम से खोजें...' : 'Search by crop (e.g. Wheat, Potato) or disease name...'}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="library-search-input"
            />
            {searchQuery && (
              <button className="clear-search-btn" onClick={() => setSearchQuery('')}>×</button>
            )}
          </div>

          {/* Priority Crop Filter Pills */}
          <div className="crop-filter-pills">
            {priorityCrops.map((crop) => (
              <button
                key={crop}
                className={`filter-pill ${selectedCropFilter === crop ? 'active' : ''}`}
                onClick={() => setSelectedCropFilter(crop)}
              >
                {crop}
              </button>
            ))}
          </div>
        </div>

        {/* Disease Cards Grid */}
        {filteredDiseases.length > 0 ? (
          <div className="disease-grid">
            {filteredDiseases.map((item, idx) => (
              <div key={idx} className="disease-card animate-fade-in">
                <div className="card-top-header">
                  <span className="plant-tag">🌿 {lang === 'hi' && item.cropHindi ? item.cropHindi : item.crop}</span>
                  <span className={`sev-tag ${item.severity?.toLowerCase()}`}>{item.severity || 'Moderate'}</span>
                </div>

                <h3 className="card-disease-title">
                  {lang === 'hi' && item.diseaseHindi ? item.diseaseHindi : item.disease}
                </h3>

                {/* Symptoms Snippet */}
                <div className="card-symptoms-snippet">
                  <div className="snippet-label">
                    <Stethoscope size={14} />
                    <span>{t.symptomsTitle}</span>
                  </div>
                  <ul className="snippet-list">
                    {((lang === 'hi' && item.symptomsHindi) ? item.symptomsHindi : item.symptoms).slice(0, 2).map((sym, sIdx) => (
                      <li key={sIdx}>{sym}</li>
                    ))}
                  </ul>
                </div>

                {/* Prevention Snippet */}
                <div className="card-prevention-snippet">
                  <div className="snippet-label">
                    <ShieldCheck size={14} />
                    <span>{t.preventionTitle}</span>
                  </div>
                  <p className="prevention-text">{item.prevention[0]}</p>
                </div>

                {/* Card Action Footer */}
                <div className="card-actions-footer">
                  <button 
                    className="btn-details-modal"
                    onClick={() => setSelectedDiseaseModal(item)}
                  >
                    <span>{lang === 'hi' ? 'विवरण देखें' : 'View Details'}</span>
                  </button>

                  <button 
                    className="btn-detect-crop"
                    onClick={() => onSelectCropForDetection(item.crop)}
                    title={`Diagnose ${item.crop}`}
                  >
                    <Sparkles size={14} />
                    <span>{t.analyzeBtn}</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-results-box">
            <p>
              {lang === 'hi' 
                ? `"${searchQuery}" से मेल खाता कोई रोग नहीं मिला। कृपया दूसरी फसल का नाम खोजें।` 
                : `No crop diseases found matching "${searchQuery}". Try another crop keyword.`}
            </p>
          </div>
        )}

        {/* Detail Modal */}
        {selectedDiseaseModal && (
          <div className="modal-backdrop" onClick={() => setSelectedDiseaseModal(null)}>
            <div className="modal-content animate-fade-in" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <div>
                  <span className="plant-tag">🌿 {selectedDiseaseModal.crop}</span>
                  <h2 className="modal-title">
                    {lang === 'hi' && selectedDiseaseModal.diseaseHindi ? selectedDiseaseModal.diseaseHindi : selectedDiseaseModal.disease}
                  </h2>
                </div>
                <button className="btn-close-modal" onClick={() => setSelectedDiseaseModal(null)}>×</button>
              </div>

              <div className="modal-body">
                <div className="modal-section">
                  <h4 className="modal-section-title">
                    <Stethoscope size={18} className="icon-symptom" />
                    {t.symptomsTitle}
                  </h4>
                  <ul className="modal-list">
                    {((lang === 'hi' && selectedDiseaseModal.symptomsHindi) ? selectedDiseaseModal.symptomsHindi : selectedDiseaseModal.symptoms).map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </div>

                <div className="modal-section">
                  <h4 className="modal-section-title">
                    <ShieldCheck size={18} className="icon-prevention" />
                    {t.culturalTitle}
                  </h4>
                  <ul className="modal-list">
                    {selectedDiseaseModal.culturalManagement?.map((c, i) => (
                      <li key={i}>{c}</li>
                    ))}
                  </ul>
                </div>

                <div className="modal-section">
                  <h4 className="modal-section-title">
                    <ShieldCheck size={18} className="icon-prevention" />
                    {t.preventionTitle}
                  </h4>
                  <ul className="modal-list">
                    {selectedDiseaseModal.prevention.map((p, i) => (
                      <li key={i}>{p}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="modal-footer">
                <button 
                  className="btn-modal-action"
                  onClick={() => {
                    setSelectedDiseaseModal(null);
                    onSelectCropForDetection(selectedDiseaseModal.crop);
                  }}
                >
                  <Sparkles size={16} />
                  <span>{t.analyzeBtn} ({selectedDiseaseModal.crop})</span>
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </section>
  );
}
