import React, { useState, useRef, useEffect } from 'react';
import { Upload, Camera, Image as ImageIcon, X, AlertCircle, CheckCircle2, Sparkles, FileText, MapPin, Sprout } from 'lucide-react';
import { translations } from '../utils/translations';
import { fetchDistrictsApi, fetchCropsApi } from '../services/plantApi';
import './ImageUploader.css';

export default function ImageUploader({ onAnalyze, isAnalyzing, lang = 'en' }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  // Location and Crop selection state
  const [districts, setDistricts] = useState([]);
  const [crops, setCrops] = useState([]);
  const [selectedDistrict, setSelectedDistrict] = useState('Lucknow');
  const [selectedCrop, setSelectedCrop] = useState('');

  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const t = translations[lang] || translations.en;

  useEffect(() => {
    // Fetch UP districts and supported crops
    async function loadMetadata() {
      const dList = await fetchDistrictsApi();
      if (dList.length > 0) setDistricts(dList);
      
      const cList = await fetchCropsApi();
      if (cList.length > 0) setCrops(cList);
    }
    loadMetadata();
  }, []);

  const validateAndSetFile = (file) => {
    setErrorMessage(null);

    if (!file) {
      setErrorMessage("Please upload a clear image where the affected leaf is visible.");
      return false;
    }

    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type.toLowerCase())) {
      setErrorMessage("Unsupported image format. Please upload a JPG, JPEG, PNG, or WebP file.");
      return false;
    }

    const MAX_SIZE_BYTES = 10 * 1024 * 1024;
    if (file.size > MAX_SIZE_BYTES) {
      setErrorMessage("Image file is too large (max 10MB). Please select a smaller file.");
      return false;
    }

    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
    return true;
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) validateAndSetFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleRemoveImage = () => {
    setSelectedFile(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setErrorMessage(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
    if (cameraInputRef.current) cameraInputRef.current.value = "";
  };

  const handleStartAnalysis = () => {
    if (!selectedFile) {
      setErrorMessage("Please upload a clear leaf image.");
      return;
    }
    onAnalyze(selectedFile, selectedDistrict, selectedCrop);
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  };

  return (
    <div className="uploader-card-container">
      <div className="uploader-card">

        {/* Section Header */}
        <div className="uploader-header">
          <div className="uploader-title-wrapper">
            <span className="uploader-icon-bg">🌿</span>
            <div>
              <h2 className="uploader-title">{t.uploaderTitle}</h2>
              <p className="uploader-subtitle">{t.uploaderSub}</p>
            </div>
          </div>
        </div>

        {/* Location & Crop Selection Controls */}
        <div className="location-selector-grid">
          <div className="selector-group">
            <label className="selector-label">
              <MapPin size={14} />
              <span>{t.stateLabel}</span>
            </label>
            <input 
              type="text" 
              value={t.stateDefault} 
              readOnly 
              className="selector-input-readonly"
            />
          </div>

          <div className="selector-group">
            <label className="selector-label">
              <MapPin size={14} />
              <span>{t.districtLabel}</span>
            </label>
            <select 
              className="selector-select"
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

          <div className="selector-group">
            <label className="selector-label">
              <Sprout size={14} />
              <span>{t.cropLabel}</span>
            </label>
            <select 
              className="selector-select"
              value={selectedCrop}
              onChange={(e) => setSelectedCrop(e.target.value)}
            >
              <option value="">{t.autoDetectCrop}</option>
              {crops.map((c) => (
                <option key={c.id} value={c.name}>
                  {c.icon} {lang === 'hi' ? c.hindiName : c.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Image Quality Error Banner */}
        {errorMessage && (
          <div className="uploader-error-box animate-fade-in">
            <AlertCircle className="error-icon" size={20} />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Dropzone OR Preview */}
        {!previewUrl ? (
          <div
            className={`uploader-dropzone ${isDragOver ? 'drag-over' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="dropzone-content">
              <div className="dropzone-icon-circle">
                <Upload className="dropzone-icon" size={36} />
              </div>

              <h3 className="dropzone-heading">
                {lang === 'hi' ? 'यहाँ अपनी फसल की पत्ती की फोटो लाएं (Drag & Drop)' : 'Drag & Drop your leaf image here'}
              </h3>
              <p className="dropzone-sub">JPG, JPEG, PNG, WebP (Max: 10MB)</p>

              {/* Action Buttons */}
              <div className="uploader-buttons">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept="image/png, image/jpeg, image/jpg, image/webp"
                  className="hidden-file-input"
                />
                <button
                  type="button"
                  className="btn-upload-choice"
                  onClick={() => fileInputRef.current && fileInputRef.current.click()}
                >
                  <ImageIcon size={18} />
                  <span>{t.chooseImage}</span>
                </button>

                <input
                  type="file"
                  ref={cameraInputRef}
                  onChange={handleFileChange}
                  accept="image/*"
                  capture="environment"
                  className="hidden-file-input"
                />
                <button
                  type="button"
                  className="btn-camera-choice"
                  onClick={() => cameraInputRef.current && cameraInputRef.current.click()}
                >
                  <Camera size={18} />
                  <span>{t.takePhoto}</span>
                </button>
              </div>

              <div className="uploader-tips">
                <span>💡 <strong>{t.tipTitle}</strong> {t.tipText}</span>
              </div>
            </div>
          </div>
        ) : (
          /* Preview Mode */
          <div className="preview-container animate-fade-in">
            <div className="preview-image-wrapper">
              <img src={previewUrl} alt="Leaf Preview" className="preview-img" />
              <button className="btn-remove-img" onClick={handleRemoveImage} title="Remove image">
                <X size={18} />
              </button>
            </div>

            <div className="preview-details">
              <div className="preview-info-row">
                <FileText size={16} className="info-icon" />
                <span className="file-name">{selectedFile?.name}</span>
                <span className="file-size">({formatFileSize(selectedFile?.size || 0)})</span>
              </div>
              <div className="preview-valid-badge">
                <CheckCircle2 size={16} />
                <span>{t.readyBadge}</span>
              </div>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="uploader-footer">
          <button
            className={`btn-analyze-submit ${isAnalyzing ? 'loading' : ''}`}
            onClick={handleStartAnalysis}
            disabled={!selectedFile || isAnalyzing}
          >
            <Sparkles size={20} />
            <span>{isAnalyzing ? t.analyzingBtn : t.analyzeBtn}</span>
          </button>
        </div>

      </div>
    </div>
  );
}
