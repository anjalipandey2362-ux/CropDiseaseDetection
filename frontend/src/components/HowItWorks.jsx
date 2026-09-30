import React from 'react';
import { Upload, Cpu, SearchCheck, ShieldAlert, ArrowRight } from 'lucide-react';
import './HowItWorks.css';

export default function HowItWorks({ onStartAnalysis, lang = 'en' }) {
  const steps = lang === 'hi' ? [
    {
      number: "01",
      title: "पत्ती का फोटो अपलोड करें",
      description: "खराब फसल की पत्ती का फोटो फोन के कैमरे से खींचें या ड्रैग करके अपलोड करें। स्थान (जिला) व फसल चुनें।",
      icon: <Upload size={28} className="step-svg" />,
      color: "step-green"
    },
    {
      number: "02",
      title: "एआई व मॉडल विश्लेषण",
      description: "फोटो एक्सप्रेस एपीआई द्वारा पाइथन FastAPI सेवा को भेजी जाती है जहां EfficientNet-B0 एआई मॉडल पत्ती के निशानों की जांच करता है।",
      icon: <Cpu size={28} className="step-svg" />,
      color: "step-blue"
    },
    {
      number: "03",
      title: "रोग व विश्वसनीयता आंकलन",
      description: "सिस्टम फसल की पहचान, संभावित रोग व विश्वसनीयता (%) का आंकलन करता है। 70% से कम विश्वसनीयता पर चेतावनी दी जाती है।",
      icon: <SearchCheck size={28} className="step-svg" />,
      color: "step-amber"
    },
    {
      number: "04",
      title: "सत्यापित उपचार व रिपोर्ट",
      description: "आईसीएआर (ICAR) व यूपी कृषि विभाग द्वारा सत्यापित दवा का नाम, मात्रा, सुरक्षा जानकारी और पीडीएफ रिपोर्ट प्राप्त करें।",
      icon: <ShieldAlert size={28} className="step-svg" />,
      color: "step-emerald"
    }
  ] : [
    {
      number: "01",
      title: "Upload Crop Leaf Photo",
      description: "Upload a clear image of the affected crop leaf using drag-and-drop or capture a live photo from your mobile device.",
      icon: <Upload size={28} className="step-svg" />,
      color: "step-green"
    },
    {
      number: "02",
      title: "AI EfficientNet Analysis",
      description: "Image is securely processed via Express API to Python FastAPI running EfficientNet-B0 transfer learning architecture.",
      icon: <Cpu size={28} className="step-svg" />,
      color: "step-blue"
    },
    {
      number: "03",
      title: "Crop & Disease Detection",
      description: "System identifies the crop species, detects possible plant diseases, and calculates an empirical confidence score.",
      icon: <SearchCheck size={28} className="step-svg" />,
      color: "step-amber"
    },
    {
      number: "04",
      title: "Verified Treatment & PDF Report",
      description: "Review verified active ingredients from ICAR/UP Ag Dept databases, safety notes, cultural care, and download PDF report.",
      icon: <ShieldAlert size={28} className="step-svg" />,
      color: "step-emerald"
    }
  ];

  return (
    <section className="how-section">
      <div className="container">
        
        {/* Section Header */}
        <div className="section-header">
          <span className="section-badge">
            <span>{lang === 'hi' ? 'सरल 4-चरण प्रक्रिया' : 'Simple 4-Step Process'}</span>
          </span>
          <h2 className="section-title">
            {lang === 'hi' ? 'प्लांटकेयर एआई कैसे काम करता है' : 'How PlantCare AI Works'}
          </h2>
          <p className="section-subtitle">
            {lang === 'hi' 
              ? 'पत्ती के फोटो से सुरक्षित एआई विश्लेषण व सत्यापित उपचार तक मात्र 3 सेकंड में।' 
              : 'From leaf photo to verified agricultural treatment in under three seconds.'}
          </p>
        </div>

        {/* Steps Grid */}
        <div className="steps-grid">
          {steps.map((step, idx) => (
            <div key={idx} className="step-card animate-fade-in">
              <div className="step-card-top">
                <div className={`step-icon-wrapper ${step.color}`}>
                  {step.icon}
                </div>
                <span className="step-number-badge">{step.number}</span>
              </div>

              <h3 className="step-card-title">{step.title}</h3>
              <p className="step-card-desc">{step.description}</p>
            </div>
          ))}
        </div>

        {/* CTA banner */}
        <div className="how-cta-banner">
          <div className="how-cta-content">
            <h3>{lang === 'hi' ? 'क्या आप अपनी फसल की जांच के लिए तैयार हैं?' : 'Ready to inspect your crop foliage?'}</h3>
            <p>{lang === 'hi' ? 'अभी पत्ती का फोटो अपलोड करें और तुरंत सलाह प्राप्त करें।' : 'Upload a leaf photo now and get immediate AI feedback.'}</p>
          </div>
          <button className="btn-how-cta" onClick={onStartAnalysis}>
            <span>{lang === 'hi' ? 'फसल की जांच करें' : 'Try Disease Detection'}</span>
            <ArrowRight size={18} />
          </button>
        </div>

      </div>
    </section>
  );
}
