import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import ImageUploader from './components/ImageUploader';
import AnalysisLoader from './components/AnalysisLoader';
import ResultCard from './components/ResultCard';
import HowItWorks from './components/HowItWorks';
import DiseaseLibrary from './components/DiseaseLibrary';
import WeatherRisk from './components/WeatherRisk';
import AIAssistant from './components/AIAssistant';
import HistorySection, { saveResultToHistory } from './components/HistorySection';
import AboutSection from './components/AboutSection';
import Footer from './components/Footer';
import { analyzePlantImageApi } from './services/plantApi';
import './App.css';

export default function App() {
  const [activePage, setActivePage] = useState('home'); // 'home' | 'detect' | 'diseases' | 'weather' | 'history' | 'about'
  const [lang, setLang] = useState('en'); // 'en' | 'hi'
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [uploadedImageUrl, setUploadedImageUrl] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);

  const toggleLanguage = () => {
    setLang(prev => prev === 'en' ? 'hi' : 'en');
  };

  const scrollToDetect = () => {
    setActivePage('detect');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const scrollToHowItWorks = () => {
    setActivePage('home');
    setTimeout(() => {
      const el = document.getElementById('how-it-works-section');
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  // Perform plant analysis trigger with location context
  const handleAnalyzeImage = async (file, selectedDistrict, selectedCrop) => {
    setIsAnalyzing(true);
    setAnalysisError(null);
    setAnalysisResult(null);

    const imageUrl = URL.createObjectURL(file);
    setUploadedImageUrl(imageUrl);

    const res = await analyzePlantImageApi(file, selectedDistrict, selectedCrop);

    setIsAnalyzing(false);

    if (res.success) {
      setAnalysisResult(res.data);
      // Save to localStorage history
      saveResultToHistory(res.data, imageUrl);
      window.scrollTo({ top: 200, behavior: 'smooth' });
    } else {
      setAnalysisError(res.error || "Analysis failed. Please check image quality and try again.");
    }
  };

  const handleResetAnalysis = () => {
    setAnalysisResult(null);
    setUploadedImageUrl(null);
    setAnalysisError(null);
  };

  const handleSelectHistoryItem = (historyItem) => {
    setAnalysisResult(historyItem);
    setUploadedImageUrl(historyItem.thumbnail || null);
    setActivePage('detect');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectCropForDetection = (cropName) => {
    setActivePage('detect');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="app-root">
      {/* Navigation Header */}
      <Navbar 
        activePage={activePage} 
        setActivePage={setActivePage} 
        onNavigateToDetect={scrollToDetect}
        lang={lang}
        onToggleLang={toggleLanguage}
      />

      <main className="app-main">

        {/* Home Page View */}
        {activePage === 'home' && (
          <>
            <Hero 
              onAnalyzeClick={scrollToDetect} 
              onHowItWorksClick={scrollToHowItWorks} 
              lang={lang}
            />

            {/* Disease Detection Main Card Container */}
            <section id="detection-tool" className="section-padding">
              <div className="container">
                {isAnalyzing ? (
                  <AnalysisLoader lang={lang} />
                ) : analysisResult ? (
                  <ResultCard 
                    resultData={analysisResult} 
                    uploadedImageUrl={uploadedImageUrl} 
                    onReset={handleResetAnalysis} 
                    lang={lang}
                  />
                ) : (
                  <ImageUploader 
                    onAnalyze={handleAnalyzeImage} 
                    isAnalyzing={isAnalyzing} 
                    lang={lang}
                  />
                )}
                {analysisError && (
                  <div className="global-error-banner animate-fade-in">
                    <p>{analysisError}</p>
                  </div>
                )}
              </div>
            </section>

            <WeatherRisk lang={lang} />

            <div id="how-it-works-section">
              <HowItWorks onStartAnalysis={scrollToDetect} lang={lang} />
            </div>
            
            <DiseaseLibrary onSelectCropForDetection={handleSelectCropForDetection} lang={lang} />
            
            <AIAssistant diseaseContext={analysisResult?.disease} cropContext={analysisResult?.crop} lang={lang} />

            <HistorySection onSelectHistoryItem={handleSelectHistoryItem} lang={lang} />

            <AboutSection lang={lang} />
          </>
        )}

        {/* Detect Page View */}
        {activePage === 'detect' && (
          <section className="section-padding min-h-page">
            <div className="container">
              <div className="page-header text-center mb-8">
                <h1 className="page-title">
                  {lang === 'hi' ? 'उत्तर प्रदेश फसल रोग जांच' : 'Plant Disease Detection'}
                </h1>
                <p className="page-subtitle">
                  {lang === 'hi'
                    ? 'अपनी फसल की पत्ती का फोटो लें या अपलोड करें और तुरंत एआई निदान प्राप्त करें।'
                    : 'Upload or take a picture of your crop leaf for immediate AI diagnosis and verified ICAR treatment.'}
                </p>
              </div>

              {isAnalyzing ? (
                <AnalysisLoader lang={lang} />
              ) : analysisResult ? (
                <ResultCard 
                  resultData={analysisResult} 
                  uploadedImageUrl={uploadedImageUrl} 
                  onReset={handleResetAnalysis} 
                  lang={lang}
                />
              ) : (
                <ImageUploader 
                  onAnalyze={handleAnalyzeImage} 
                  isAnalyzing={isAnalyzing} 
                  lang={lang}
                />
              )}

              {analysisError && (
                <div className="global-error-banner animate-fade-in">
                  <p>{analysisError}</p>
                </div>
              )}
            </div>
          </section>
        )}

        {/* Diseases Page View */}
        {activePage === 'diseases' && (
          <DiseaseLibrary onSelectCropForDetection={handleSelectCropForDetection} lang={lang} />
        )}

        {/* Weather Risk View */}
        {activePage === 'weather' && (
          <WeatherRisk lang={lang} />
        )}

        {/* History Page View */}
        {activePage === 'history' && (
          <HistorySection onSelectHistoryItem={handleSelectHistoryItem} lang={lang} />
        )}

        {/* About Page View */}
        {activePage === 'about' && (
          <AboutSection lang={lang} />
        )}

      </main>

      {/* Footer */}
      <Footer 
        onNavigate={(page) => {
          setActivePage(page);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
        lang={lang}
      />
    </div>
  );
}
