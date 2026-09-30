import React, { useState, useEffect } from 'react';
import { CloudRain, Thermometer, Droplets, AlertTriangle, ShieldCheck, MapPin, Info } from 'lucide-react';
import { fetchWeatherRiskApi, fetchDistrictsApi } from '../services/plantApi';
import { translations } from '../utils/translations';
import './WeatherRisk.css';

export default function WeatherRisk({ lang = 'en' }) {
  const [selectedDistrict, setSelectedDistrict] = useState('Lucknow');
  const [districts, setDistricts] = useState([]);
  const [weatherData, setWeatherData] = useState(null);

  const t = translations[lang] || translations.en;

  useEffect(() => {
    async function loadDistricts() {
      const dList = await fetchDistrictsApi();
      if (dList.length > 0) setDistricts(dList);
    }
    loadDistricts();
  }, []);

  useEffect(() => {
    async function loadRisk() {
      const data = await fetchWeatherRiskApi(selectedDistrict);
      if (data) setWeatherData(data);
    }
    loadRisk();
  }, [selectedDistrict]);

  const getRiskClass = (level) => {
    if (level === 'High') return 'risk-high';
    if (level === 'Moderate') return 'risk-mod';
    return 'risk-low';
  };

  return (
    <section className="weather-section">
      <div className="container">
        <div className="weather-card-container animate-fade-in">

          {/* Header */}
          <div className="weather-header">
            <div className="weather-title-group">
              <span className="weather-icon-badge">🌦️</span>
              <div>
                <h3 className="weather-title">
                  {lang === 'hi' ? 'उत्तर प्रदेश फसल रोग मौसम जोखिम' : 'UP Crop Disease Risk Forecast'}
                </h3>
                <p className="weather-sub">
                  {lang === 'hi' ? 'तापमान, नमी व बारिश आधारित फफूंद प्रसार जोखिम आंकलन' : 'Humidity & temperature based disease propagation risk model'}
                </p>
              </div>
            </div>

            <div className="district-selector-inline">
              <MapPin size={16} className="text-emerald-600" />
              <select
                className="district-select-dropdown"
                value={selectedDistrict}
                onChange={(e) => setSelectedDistrict(e.target.value)}
              >
                {districts.map((d) => (
                  <option key={d.id} value={d.name}>
                    {lang === 'hi' ? d.hindiName : d.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Indicators Grid */}
          {weatherData && (
            <>
              <div className="weather-metrics-grid">
                <div className="metric-card">
                  <span className="metric-label">
                    <Thermometer size={16} />
                    <span>{lang === 'hi' ? 'तापमान' : 'Temperature'}</span>
                  </span>
                  <span className="metric-val">{weatherData.temperature}</span>
                </div>

                <div className="metric-card">
                  <span className="metric-label">
                    <Droplets size={16} />
                    <span>{lang === 'hi' ? 'सापेक्ष आर्द्रता' : 'Humidity'}</span>
                  </span>
                  <span className="metric-val">{weatherData.humidity}</span>
                </div>

                <div className="metric-card">
                  <span className="metric-label">
                    <AlertTriangle size={16} />
                    <span>{lang === 'hi' ? 'रोग जोखिम स्तर' : 'Fungal Risk'}</span>
                  </span>
                  <span className={`risk-level-pill ${getRiskClass(weatherData.riskLevel)}`}>
                    {weatherData.riskLevel}
                  </span>
                </div>
              </div>

              {/* Forecast Advisory */}
              <div className="weather-forecast-box">
                <span className="forecast-title">
                  💡 {lang === 'hi' ? 'मौसमी कृषि सलाह:' : 'Seasonal Agricultural Advisory:'}
                </span>
                <p style={{ fontSize: '0.92rem', color: '#064e3b', fontWeight: 500 }}>
                  {weatherData.forecastMessage}
                </p>

                {weatherData.highRiskDiseases && weatherData.highRiskDiseases.length > 0 && (
                  <div>
                    <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#047857' }}>
                      {lang === 'hi' ? 'वर्तमान मौसम में सतर्क योग्य रोग:' : 'Diseases requiring monitoring this season:'}
                    </span>
                    <div className="high-risk-crops-list">
                      {weatherData.highRiskDiseases.map((d, i) => (
                        <span key={i} className="high-risk-chip">⚠️ {d}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </>
          )}

          {/* Mandatory Disclaimer */}
          <div className="weather-disclaimer">
            <Info size={16} className="flex-shrink-0" />
            <p>
              <strong>Disclaimer:</strong> {weatherData?.disclaimer || "Weather indicators provide crop disease risk context only and do not confirm disease presence in specific fields."}
            </p>
          </div>

        </div>
      </div>
    </section>
  );
}
