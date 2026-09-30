import React, { useState, useEffect } from 'react';
import { Loader2, CheckCircle2, Circle } from 'lucide-react';
import { translations } from '../utils/translations';
import './AnalysisLoader.css';

export default function AnalysisLoader({ lang = 'en' }) {
  const [currentStep, setCurrentStep] = useState(0);

  const t = translations[lang] || translations.en;

  const steps = [
    { label: t.step1, icon: "🌱" },
    { label: t.step2, icon: "🔍" },
    { label: t.step3, icon: "🧠" },
    { label: t.step4, icon: "📊" },
    { label: t.step5, icon: "💊" }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < steps.length - 1) return prev + 1;
        return prev;
      });
    }, 600);

    return () => clearInterval(interval);
  }, [steps.length]);

  return (
    <div className="loader-overlay animate-fade-in">
      <div className="loader-card">
        {/* Main Animated Icon */}
        <div className="loader-spinner-wrapper">
          <div className="pulse-ring"></div>
          <Loader2 className="spinner-icon animate-spin-slow" size={48} />
          <span className="spinner-emoji">🌾</span>
        </div>

        <h3 className="loader-title">
          {lang === 'hi' ? 'फसल की फोटो का विश्लेषण हो रहा है...' : 'Analyzing crop image...'}
        </h3>
        <p className="loader-subtitle">
          {lang === 'hi' 
            ? 'EfficientNet एआई मॉडल रोग के निशानों की जांच कर रहा है।' 
            : 'Please hold on while EfficientNet model evaluates the leaf.'}
        </p>

        {/* Animated Steps Checklist */}
        <div className="loader-steps-list">
          {steps.map((step, idx) => {
            const isDone = idx < currentStep;
            const isCurrent = idx === currentStep;

            return (
              <div
                key={idx}
                className={`loader-step-item ${isDone ? 'done' : ''} ${isCurrent ? 'active' : ''}`}
              >
                <div className="step-status">
                  {isDone ? (
                    <CheckCircle2 className="step-icon-done" size={20} />
                  ) : isCurrent ? (
                    <Loader2 className="step-icon-active animate-spin-slow" size={20} />
                  ) : (
                    <Circle className="step-icon-pending" size={20} />
                  )}
                </div>

                <div className="step-text-wrapper">
                  <span className="step-emoji">{step.icon}</span>
                  <span className="step-text">{step.label}</span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="loader-progress-bar-track">
          <div
            className="loader-progress-bar-fill"
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}
