import React, { useState } from 'react';
import { 
  CheckCircle2, 
  RotateCcw, 
  Download, 
  Share2, 
  Leaf, 
  Stethoscope, 
  ShieldCheck, 
  Info,
  Check,
  Pill,
  BookOpen,
  MapPin,
  ShieldAlert,
  Terminal,
  Bug,
  AlertTriangle
} from 'lucide-react';
import jsPDF from 'jspdf';
import { translations } from '../utils/translations';
import './ResultCard.css';

export default function ResultCard({ resultData, uploadedImageUrl, onReset, lang = 'en' }) {
  const [copied, setCopied] = useState(false);
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);

  const t = translations[lang] || translations.en;

  if (!resultData) return null;

  const {
    status = "success",
    crop = null,
    cropHindi = null,
    cropConfidence = 0.0,
    disease = null,
    diseaseHindi = null,
    diseaseConfidence = 0.0,
    confidence = 0.0,
    isLowConfidence = false,
    severity = "Moderate",
    symptoms = [],
    symptomsHindi = [],
    verifiedTreatment = null,
    treatmentMessage = null,
    culturalManagement = [],
    prevention = [],
    supportedCrops = [],
    topPredictions = [],
    isDevMode = false,
    debug = null,
    message = null,
    district = "Lucknow"
  } = resultData;

  const parseConfidencePct = (val) => {
    if (val === null || val === undefined || isNaN(val)) return 0;
    const num = Number(val);
    if (num <= 1.0) return Math.round(num * 10000) / 100;
    return Math.round(num * 100) / 100;
  };

  const confidencePercentage = resultData.confidence_percent !== undefined 
    ? Math.round(Number(resultData.confidence_percent) * 100) / 100 
    : parseConfidencePct(confidence || cropConfidence || 0);

  const cropConfPct = parseConfidencePct(cropConfidence || confidence || 0);
  const diseaseConfPct = parseConfidencePct(diseaseConfidence || confidence || 0);

  const displayCrop = crop ? (lang === 'hi' && cropHindi ? cropHindi : crop) : (lang === 'hi' ? 'अज्ञात फसल' : 'Unknown Crop');
  const displayDisease = disease ? (lang === 'hi' && diseaseHindi ? diseaseHindi : disease) : (lang === 'hi' ? 'अज्ञात रोग' : 'Uncertain Disease');
  const displaySymptoms = (lang === 'hi' && symptomsHindi && symptomsHindi.length > 0) ? symptomsHindi : symptoms;

  const isUncertain = isLowConfidence || status === 'uncertain_crop' || status === 'uncertain_disease' || status === 'uncertain_mismatch' || status === 'non_plant';
  const isUnsupported = status === 'unsupported_crop';

  const getConfidenceLabel = (pct) => {
    if (isUncertain || pct < 70) return t.lowConfidence;
    if (pct >= 85) return t.highConfidence;
    return t.modConfidence;
  };

  const getSeverityBadge = (sev) => {
    if (isUncertain || isUnsupported || !disease) return { label: lang === 'hi' ? 'अनुपलब्ध' : 'Not available', class: 'sev-unknown' };
    const s = (sev || '').toLowerCase();
    if (s.includes('high') || s.includes('severe')) return { label: lang === 'hi' ? '🔴 गंभीर (High)' : '🔴 High', class: 'sev-high' };
    if (s.includes('mod')) return { label: lang === 'hi' ? '🟡 मध्यम (Moderate)' : '🟡 Moderate', class: 'sev-moderate' };
    if (s.includes('low')) return { label: lang === 'hi' ? '🟢 हल्का (Low)' : '🟢 Low', class: 'sev-low' };
    if (s.includes('none') || s.includes('healthy')) return { label: lang === 'hi' ? '🌱 स्वस्थ (None)' : '🌱 Healthy / None', class: 'sev-none' };
    return { label: lang === 'hi' ? 'अनुपलब्ध' : 'Not available', class: 'sev-unknown' };
  };

  const severityInfo = getSeverityBadge(severity);

  // PDF Report Generation
  const handleDownloadPdf = async () => {
    setIsGeneratingPdf(true);
    try {
      const pdf = new jsPDF('p', 'mm', 'a4');
      const margin = 15;
      let yPos = 20;

      pdf.setFillColor(22, 163, 74);
      pdf.rect(0, 0, 210, 28, 'F');
      pdf.setTextColor(255, 255, 255);
      pdf.setFont('helvetica', 'bold');
      pdf.setFontSize(18);
      pdf.text("PlantCare AI - Crop Diagnostic Report", margin, 18);

      pdf.setTextColor(15, 23, 42);
      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'normal');

      yPos = 38;
      pdf.text(`Report Date: ${new Date().toLocaleDateString()} | Location: ${district}, Uttar Pradesh`, margin, yPos);
      
      yPos += 10;
      pdf.setLineWidth(0.5);
      pdf.setDrawColor(22, 163, 74);
      pdf.line(margin, yPos, 210 - margin, yPos);

      yPos += 12;
      pdf.setFont('helvetica', 'bold');
      pdf.setFontSize(12);
      pdf.text("1. Diagnostic Summary", margin, yPos);

      yPos += 8;
      pdf.setFontSize(10);
      pdf.text(`Crop Identified: ${crop || "Unknown"} (${cropConfPct}%)`, margin, yPos);
      pdf.text(`Status: ${status.toUpperCase()}`, margin + 85, yPos);
      
      yPos += 6;
      pdf.text(`Detected Disease: ${disease || "Outside Model / Uncertain"} (${diseaseConfPct}%)`, margin, yPos);

      yPos += 12;
      if (isUnsupported) {
        pdf.setFillColor(240, 253, 244);
        pdf.rect(margin, yPos, 180, 20, 'F');
        pdf.setTextColor(22, 101, 52);
        pdf.setFont('helvetica', 'bold');
        pdf.text(`OUT-OF-SCOPE CROP: ${crop}`, margin + 5, yPos + 7);
        pdf.setFont('helvetica', 'normal');
        pdf.text("This crop is currently outside the active agricultural disease-detection model.", margin + 5, yPos + 13);
        yPos += 26;
      } else if (isUncertain) {
        pdf.setFillColor(254, 243, 199);
        pdf.rect(margin, yPos, 180, 18, 'F');
        pdf.setTextColor(146, 64, 14);
        pdf.setFont('helvetica', 'bold');
        pdf.text("LOW CONFIDENCE / UNCERTAIN WARNING:", margin + 5, yPos + 7);
        pdf.setFont('helvetica', 'normal');
        pdf.text(message || "AI confidence is below threshold. Chemical treatments are omitted.", margin + 5, yPos + 13);
        yPos += 24;
      } else if (verifiedTreatment) {
        pdf.setFont('helvetica', 'bold');
        pdf.setFontSize(12);
        pdf.setTextColor(15, 23, 42);
        pdf.text("2. Recommended Verified Treatment (ICAR / UP Ag Dept)", margin, yPos);

        yPos += 8;
        pdf.setFontSize(10);
        pdf.text(`Treatment Type: ${verifiedTreatment.treatmentType}`, margin, yPos);
        yPos += 6;
        pdf.text(`Active Ingredient: ${verifiedTreatment.activeIngredient}`, margin, yPos);
        yPos += 6;
        pdf.text(`Registered Product: ${verifiedTreatment.productName}`, margin, yPos);
        yPos += 6;
        pdf.setFont('helvetica', 'normal');
        const splitGuidance = pdf.splitTextToSize(`Application Guidance: ${verifiedTreatment.applicationGuidance}`, 180);
        pdf.text(splitGuidance, margin, yPos);
        yPos += (splitGuidance.length * 5) + 2;

        pdf.setFont('helvetica', 'italic');
        pdf.text(`Verified Source: ${verifiedTreatment.source} (Verified: ${verifiedTreatment.lastVerified})`, margin, yPos);
        yPos += 8;
      }

      pdf.save(`PlantCare-Report-${crop || 'Crop'}.pdf`);
    } catch (err) {
      console.error("PDF generation error:", err);
      window.print();
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  const handleShare = async () => {
    const shareText = `PlantCare AI Diagnosis:\nCrop: ${displayCrop} (${cropConfPct}%)\nCondition: ${displayDisease}\nDistrict: ${district}\n\nAnalyzed with PlantCare AI.`;

    if (navigator.share) {
      try {
        await navigator.share({
          title: `PlantCare AI: ${displayCrop}`,
          text: shareText,
          url: window.location.href
        });
        return;
      } catch (e) {}
    }

    navigator.clipboard.writeText(shareText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="result-container animate-fade-in">
      <div id="printable-result-card" className="result-card">

        {/* Header & Status Banner */}
        <div className="result-header">
          <div className="header-left">
            <span className="result-chip">
              <Leaf size={16} />
              <span>Independent Two-Stage Vision Pipeline</span>
            </span>
            {isDevMode && (
              <span className="simulated-badge" title="Development Mode — Connect trained models in ml-service/models/">
                {t.devModeBadge}
              </span>
            )}
            <span className="source-badge">
              <MapPin size={13} />
              <span>{district}, Uttar Pradesh</span>
            </span>
          </div>
          <div className="timestamp">
            {new Date().toLocaleDateString(lang === 'hi' ? 'hi-IN' : 'en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
          </div>
        </div>

        {/* Summary Banner */}
        <div className="summary-banner">
          {uploadedImageUrl && (
            <div className="result-image-box">
              <img src={uploadedImageUrl} alt="Uploaded Crop Leaf" className="result-leaf-img" />
            </div>
          )}

          <div className="summary-details">
            <div className="detected-plant-row">
              <span className="label-caption">{t.plantIdentified}</span>
              <h2 className="detected-plant-name">
                {displayCrop} {cropConfPct ? `(${cropConfPct}%)` : ''}
              </h2>
            </div>

            <div className="detected-disease-row">
              <span className="label-caption">{t.detectedDiagnosis}</span>
              <h3 className="detected-disease-name">
                {isUnsupported ? (lang === 'hi' ? 'रोग मॉडल सीमा के बाहर' : 'Outside Disease Model Scope') : (disease ? `${displayDisease} (${diseaseConfPct}%)` : (lang === 'hi' ? 'रोग अनिश्चित' : 'Uncertain Disease'))}
              </h3>
            </div>

            <div className="severity-row">
              <span className="label-caption">{t.severityLevel}</span>
              <span className={`severity-badge ${severityInfo.class}`}>
                {severityInfo.label}
              </span>
            </div>
          </div>

          {/* Confidence Gauge */}
          <div className="confidence-gauge-box">
            <div className="gauge-circle" style={{ '--percent': confidencePercentage }}>
              <svg className="ring-svg" viewBox="0 0 36 36">
                <path
                  className="circle-bg"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className="circle-fill"
                  strokeDasharray={`${confidencePercentage}, 100`}
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  stroke={isUncertain ? '#eab308' : (isUnsupported ? '#0284c7' : '#22c55e')}
                />
              </svg>
              <div className="gauge-text">
                <span className="gauge-number">{confidencePercentage}%</span>
                <span className="gauge-sub">{t.accuracy}</span>
              </div>
            </div>
            <span className="confidence-status">{getConfidenceLabel(confidencePercentage)}</span>
          </div>
        </div>

        {/* STATE B: UNSUPPORTED / OUT-OF-SCOPE CROP (e.g. Apple, Tomato) */}
        {isUnsupported && (
          <div className="unsupported-crop-card animate-fade-in">
            <div className="unsupported-header">
              <AlertTriangle size={24} className="text-emerald-700 flex-shrink-0" />
              <h3 className="unsupported-title">
                {lang === 'hi' ? `${displayCrop} पहचाना गया` : `${crop} Detected`}
              </h3>
            </div>
            <p className="unsupported-msg">
              {message || (lang === 'hi' 
                ? `यह फसल (${displayCrop}) वर्तमान में हमारे सक्रिय फसल रोग-निदान मॉडल के दायरे से बाहर है।` 
                : `${crop} is currently outside the supported agricultural disease-detection model.`)}
            </p>

            <div className="supported-crops-box">
              <span className="supported-crops-label">
                {lang === 'hi' ? 'वर्तमान में समर्थित कृषि फसलें:' : 'Currently Supported Agricultural Crops:'}
              </span>
              <div className="supported-chips-flex">
                {supportedCrops.map((cName, idx) => (
                  <span key={idx} className="supported-crop-chip">🌾 {cName}</span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* STATE C / D / E: UNCERTAIN CROP, NON-PLANT, OR LOW DISEASE CONFIDENCE */}
        {isUncertain && !isUnsupported && (
          <div className="low-confidence-banner animate-fade-in">
            <ShieldAlert className="low-confidence-icon" size={28} />
            <div className="low-confidence-content">
              <h4>
                {status === 'uncertain_crop' ? (lang === 'hi' ? '⚠️ फसल की पहचान अनिश्चित' : '⚠️ Crop Could Not Be Identified Confidently') :
                 status === 'non_plant' ? (lang === 'hi' ? '⚠️ कोई फसल या पौधा नहीं मिला' : '⚠️ No Supported Plant/Crop Detected') :
                 (lang === 'hi' ? '⚠️ रोग की पहचान अनिश्चित' : '⚠️ Disease Identification Uncertain')}
              </h4>
              <p>{message || t.lowConfidenceWarningMsg}</p>
              <p style={{ marginTop: '6px', fontWeight: 600 }}>{t.noChemicalLowConf}</p>
            </div>
          </div>
        )}

        {/* STATE A: VERIFIED RECOMMENDED TREATMENT SECTION (Supported Crops Only) */}
        {status === 'success' && !isUncertain && !isUnsupported && (
          <div className="verified-treatment-section animate-fade-in">
            <div className="verified-treatment-header">
              <div className="verified-title-group">
                <Pill size={22} className="text-emerald-600" />
                <h3>{t.treatmentTitle}</h3>
              </div>
              {verifiedTreatment && (
                <span className="source-badge">
                  <BookOpen size={14} />
                  <span>{verifiedTreatment.source}</span>
                </span>
              )}
            </div>

            {verifiedTreatment ? (
              <>
                <div className="treatment-details-grid">
                  <div className="treatment-detail-card primary-active">
                    <span className="detail-label">{t.activeIngredient}</span>
                    <span className="detail-value-highlight">{verifiedTreatment.activeIngredient}</span>
                  </div>

                  <div className="treatment-detail-card">
                    <span className="detail-label">{t.productName}</span>
                    <span className="detail-value-text">{verifiedTreatment.productName}</span>
                  </div>

                  <div className="treatment-detail-card">
                    <span className="detail-label">{t.treatmentType}</span>
                    <span className="detail-value-text">{verifiedTreatment.treatmentType}</span>
                  </div>

                  <div className="treatment-detail-card">
                    <span className="detail-label">{t.sourceLabel}</span>
                    <span className="detail-value-text">{verifiedTreatment.source} (Verified: {verifiedTreatment.lastVerified})</span>
                  </div>
                </div>

                <div className="treatment-detail-card">
                  <span className="detail-label">{t.applicationGuidance}</span>
                  <span className="detail-value-text" style={{ fontSize: '0.95rem' }}>
                    {verifiedTreatment.applicationGuidance}
                  </span>
                </div>

                {verifiedTreatment.biologicalTreatment && (
                  <div className="treatment-detail-card" style={{ background: '#f0fdf4', borderColor: '#bbf7d0' }}>
                    <span className="detail-label">{t.bioTreatmentTitle}</span>
                    <span className="detail-value-text">{verifiedTreatment.biologicalTreatment}</span>
                  </div>
                )}

                <div className="safety-warning-box">
                  <Info size={18} className="flex-shrink-0" />
                  <div>
                    <strong>{t.safetyInfo}</strong> {verifiedTreatment.safetyInformation}
                    <div style={{ marginTop: '4px', fontWeight: 700, textDecoration: 'underline' }}>
                      {t.safetyDisclaimer}
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <p className="no-data">{treatmentMessage || t.noVerifiedTreatmentMsg}</p>
            )}
          </div>
        )}

        {/* Symptoms, Cultural Management, Prevention Grid */}
        {!isUnsupported && !isUncertain && (
          <div className="result-grid">
            <div className="grid-card symptoms-card">
              <div className="grid-card-header">
                <Stethoscope className="card-header-icon symptoms" size={20} />
                <h4>{t.symptomsTitle}</h4>
              </div>
              {displaySymptoms.length > 0 ? (
                <ul className="symptoms-list">
                  {displaySymptoms.map((item, idx) => (
                    <li key={idx}>
                      <span className="bullet-dot"></span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="no-data">No specific symptoms recorded for this diagnosis.</p>
              )}
            </div>

            <div className="grid-card treatment-card">
              <div className="grid-card-header">
                <Leaf className="card-header-icon treatment" size={20} />
                <h4>{t.culturalTitle}</h4>
              </div>
              {culturalManagement.length > 0 ? (
                <ul className="treatment-list">
                  {culturalManagement.map((item, idx) => (
                    <li key={idx}>
                      <CheckCircle2 size={16} className="check-icon" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="no-data">Maintain clean fields and proper plant spacing.</p>
              )}
            </div>

            <div className="grid-card prevention-card">
              <div className="grid-card-header">
                <ShieldCheck className="card-header-icon prevention" size={20} />
                <h4>{t.preventionTitle}</h4>
              </div>
              {prevention.length > 0 ? (
                <ul className="prevention-list">
                  {prevention.map((item, idx) => (
                    <li key={idx}>
                      <span className="prevention-badge-num">{idx + 1}</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="no-data">Use certified disease-resistant seeds.</p>
              )}
            </div>
          </div>
        )}

        {/* AI DEBUG SECTION IN DEVELOPMENT MODE (Requirement #11) */}
        {isDevMode && (
          <div className="ai-debug-card animate-fade-in">
            <div className="ai-debug-header">
              <div className="flex items-center gap-2">
                <Bug size={16} />
                <span>AI DEBUG (Development & Inspection Logs)</span>
              </div>
              <Terminal size={16} />
            </div>

            <div className="ai-debug-grid">
              <div className="debug-item">
                <span className="debug-key">Stage 1 Crop Prediction:</span>
                <span className="debug-val">{crop || "Unknown"} ({cropConfPct}%)</span>
              </div>

              <div className="debug-item">
                <span className="debug-key">Stage 2 Disease Prediction:</span>
                <span className="debug-val">{disease || "None / Out-of-Scope"} ({diseaseConfPct}%)</span>
              </div>

              <div className="debug-item">
                <span className="debug-key">Pipeline Status:</span>
                <span className="debug-val" style={{ color: status === 'success' ? '#4ade80' : '#facc15' }}>
                  {status.toUpperCase()}
                </span>
              </div>

              <div className="debug-item">
                <span className="debug-key">Crop Model Path:</span>
                <span className="debug-val">{debug?.crop_model || "models/crop_classifier/crop_model.pth"}</span>
              </div>

              <div className="debug-item">
                <span className="debug-key">Disease Model Path:</span>
                <span className="debug-val">{debug?.disease_model || "Outside Scope / None"}</span>
              </div>

              <div className="debug-item">
                <span className="debug-key">Consistency Verification:</span>
                <span className={`debug-val ${debug?.consistency_check === 'PASSED' ? 'passed' : ''}`}>
                  {debug?.consistency_check || (isUncertain || isUnsupported ? 'STOPPED (NO MISMATCH)' : 'PASSED')}
                </span>
              </div>
            </div>

            {/* Top-3 Predictions Debug List */}
            {topPredictions && topPredictions.length > 0 && (
              <div style={{ marginTop: '8px', borderTop: '1px solid #1e293b', paddingTop: '8px' }}>
                <span className="debug-key">Top-3 Crop Classifier Probabilities:</span>
                <div className="top-preds-list">
                  {topPredictions.map((pred, pIdx) => (
                    <span key={pIdx} className="top-pred-badge">
                      #{pIdx + 1}: {pred.crop} ({Math.round(pred.confidence * 100)}%)
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Disclaimer Notice */}
        <div className="result-disclaimer">
          <Info size={18} className="disclaimer-alert-icon" />
          <p>
            <strong>Disclaimer:</strong> PlantCare AI provides AI-assisted decision support and verified agricultural extension information. Image predictions should be verified with local agricultural extension officers when severe symptoms occur.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="result-actions-bar">
          <button className="btn-action btn-reset" onClick={onReset}>
            <RotateCcw size={18} />
            <span>{t.analyzeAnother}</span>
          </button>

          <button className="btn-action btn-pdf" onClick={handleDownloadPdf} disabled={isGeneratingPdf}>
            <Download size={18} />
            <span>{isGeneratingPdf ? "Generating PDF..." : t.downloadReport}</span>
          </button>

          <button className="btn-action btn-share" onClick={handleShare}>
            {copied ? <Check size={18} /> : <Share2 size={18} />}
            <span>{copied ? "Copied!" : t.shareResult}</span>
          </button>
        </div>

      </div>
    </div>
  );
}
