import React, { useState } from 'react';
import { Bot, Send, User, Sparkles, MessageSquare, Loader2 } from 'lucide-react';
import { askAIAssistantApi } from '../services/plantApi';
import { translations } from '../utils/translations';
import './AIAssistant.css';

export default function AIAssistant({ diseaseContext, cropContext, lang = 'en' }) {
  const t = translations[lang] || translations.en;

  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: lang === 'hi'
        ? `नमस्ते! मैं आपका प्लांटकेयर एआई कृषि सलाहकार हूँ। ${diseaseContext ? `मैं देख रहा हूँ कि आप ${diseaseContext} के बारे में पूछ रहे हैं।` : 'गेहूं, धान, गन्ना, आलू या सरसों के रोगों, लक्षणों व सत्यापित दवाओं के बारे में पूछें!'}`
        : `Hello! I am your PlantCare AI Agronomist Assistant. ${
            diseaseContext 
              ? `I see you are inquiring about ${diseaseContext}. How can I assist with verified treatment, symptoms, or prevention?`
              : 'Ask me anything about UP crop diseases, leaf symptoms, verified ICAR treatments, or prevention!'
          }`
    }
  ]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const samplePrompts = lang === 'hi' ? [
    "इस बीमारी को फैलने से कैसे रोकें?",
    "इसके मुख्य लक्षण क्या हैं?",
    "सत्यापित दवा और छिड़काव की मात्रा क्या है?",
    "क्या यह रोग अन्य फसलों में भी फैलता है?"
  ] : [
    "How can I prevent this disease?",
    "What symptoms should I monitor?",
    "What is the recommended dosage?",
    "How can I improve overall crop health?"
  ];

  const handleSend = async (questionText) => {
    const query = (questionText || inputQuestion).trim();
    if (!query || isLoading) return;

    const userMsg = { sender: 'user', text: query };
    setMessages((prev) => [...prev, userMsg]);
    setInputQuestion('');
    setIsLoading(true);

    const res = await askAIAssistantApi(query, diseaseContext, cropContext);

    const aiMsg = { sender: 'ai', text: res.reply };
    setMessages((prev) => [...prev, aiMsg]);
    setIsLoading(false);
  };

  return (
    <section className="assistant-section">
      <div className="container">
        
        <div className="section-header">
          <span className="section-badge">
            <Sparkles size={16} />
            <span>{t.assistantTitle}</span>
          </span>
          <h2 className="section-title">
            {lang === 'hi' ? 'प्लांटकेयर एआई से सवाल पूछें' : 'Ask PlantCare AI Agronomist'}
          </h2>
          <p className="section-subtitle">
            {lang === 'hi'
              ? 'फसल के रोगों, लक्षणों, सत्यापित जैविक व रासायनिक उपचार और रोकथाम गाइड के बारे में तुरंत उत्तर पाएं।'
              : 'Get instant answers regarding crop symptoms, verified ICAR treatments, and prevention strategies for UP crops.'}
          </p>
        </div>

        <div className="chat-card-container">
          <div className="chat-card">

            {/* Chat Messages Body */}
            <div className="chat-body">
              {messages.map((msg, idx) => (
                <div key={idx} className={`chat-message-row ${msg.sender}`}>
                  <div className="message-avatar">
                    {msg.sender === 'ai' ? <Bot size={20} /> : <User size={20} />}
                  </div>
                  <div className="message-bubble">
                    <p style={{ whiteSpace: 'pre-line' }}>{msg.text}</p>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="chat-message-row ai">
                  <div className="message-avatar">
                    <Bot size={20} />
                  </div>
                  <div className="message-bubble loading">
                    <Loader2 className="animate-spin-slow" size={18} />
                    <span>{lang === 'hi' ? 'कृषि डेटाबेस जांचा जा रहा है...' : 'Checking verified database...'}</span>
                  </div>
                </div>
              )}
            </div>

            {/* Quick Sample Questions */}
            <div className="sample-prompts-bar">
              <span className="prompts-label">{lang === 'hi' ? 'सुझाए गए प्रश्न:' : 'Suggested questions:'}</span>
              <div className="prompts-pills">
                {samplePrompts.map((prompt, pIdx) => (
                  <button
                    key={pIdx}
                    className="prompt-pill"
                    onClick={() => handleSend(prompt)}
                    disabled={isLoading}
                  >
                    <MessageSquare size={14} />
                    <span>{prompt}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Input Bar */}
            <div className="chat-input-bar">
              <input
                type="text"
                placeholder={lang === 'hi' ? 'फसल रोग या दवा के बारे में प्रश्न पूछें...' : 'Ask a question about crop disease or treatment...'}
                value={inputQuestion}
                onChange={(e) => setInputQuestion(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                disabled={isLoading}
                className="chat-input"
              />
              <button
                className="btn-send-chat"
                onClick={() => handleSend()}
                disabled={!inputQuestion.trim() || isLoading}
              >
                <Send size={18} />
              </button>
            </div>

          </div>
        </div>

      </div>
    </section>
  );
}
