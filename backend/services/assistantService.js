import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const treatmentsPath = path.join(__dirname, '../data/treatments.json');
const diseasesPath = path.join(__dirname, '../data/diseases.json');

const treatmentsList = JSON.parse(fs.readFileSync(treatmentsPath, 'utf8'));
const diseasesList = JSON.parse(fs.readFileSync(diseasesPath, 'utf8'));

/**
 * Handles farmer queries via AI Assistant.
 * Uses verified database information to prevent LLM hallucination of chemical pesticides.
 */
export async function processAssistantQuery(question, diseaseContext = "", cropContext = "") {
  if (!question || typeof question !== 'string') {
    return "Please enter a valid question regarding crop health or disease management.";
  }

  const qLower = question.toLowerCase();

  // Search for matching disease or treatment in verified DB
  let matchedTreatment = null;
  if (diseaseContext) {
    matchedTreatment = treatmentsList.find(t => 
      t.disease.toLowerCase().includes(diseaseContext.toLowerCase()) || 
      diseaseContext.toLowerCase().includes(t.disease.toLowerCase().split(' ')[0])
    );
  }

  // Question Intent 1: Medicine / Pesticide / Treatment
  if (qLower.includes("medicine") || qLower.includes("pesticide") || qLower.includes("chemical") || qLower.includes("fungicide") || qLower.includes("treatment") || qLower.includes("dawa") || qLower.includes("उपचार")) {
    if (matchedTreatment) {
      return `💊 Verified Treatment Information for ${matchedTreatment.disease} in ${matchedTreatment.crop}:\n\n` +
             `• Treatment Type: ${matchedTreatment.treatmentType}\n` +
             `• Active Ingredient: ${matchedTreatment.activeIngredient}\n` +
             `• Recommended Dose: ${matchedTreatment.applicationGuidance}\n` +
             `• Biological Option: ${matchedTreatment.biologicalTreatment}\n` +
             `• Safety Note: ${matchedTreatment.safetyInformation}\n` +
             `• Source: ${matchedTreatment.source} (Verified: ${matchedTreatment.lastVerified})\n\n` +
             `⚠️ Disclaimer: Always follow the registered product label and local agricultural extension guidance before application.`;
    }
    return `For chemical pesticide or fungicide recommendations, please analyze a crop leaf photo first or select a specific crop. PlantCare AI only displays verified recommendations directly from agricultural research sources (ICAR / UP Ag Dept) to ensure crop safety.`;
  }

  // Question Intent 2: Prevention / Agronomic management
  if (qLower.includes("prevent") || qLower.includes("avoid") || qLower.includes("stop") || qLower.includes("रोकथाम")) {
    if (matchedTreatment && matchedTreatment.culturalManagement) {
      return `🌱 Verified Cultural & Preventive Steps for ${matchedTreatment.crop}:\n\n` +
             `1. ${matchedTreatment.culturalManagement}\n` +
             `2. Maintain 3-year crop rotation with non-host crops.\n` +
             `3. Inspect foliage weekly during foggy morning conditions.\n` +
             `4. Use certified disease-resistant seed varieties recommended for UP.\n` +
             `5. Avoid excess nitrogenous fertilizer doses and avoid foliage wetness overnight.`;
    }
    return `Effective crop disease prevention in Uttar Pradesh involves: 1) Using certified disease-resistant seeds (e.g. HD 2967 wheat, Kufri Pukhraj potato), 2) Practicing 3-year crop rotation with pulses or oilseeds, 3) Deep summer plowing in May-June, and 4) Applying bio-control seed treatments like Trichoderma viride.`;
  }

  // Question Intent 3: Symptoms / Diagnosis
  if (qLower.includes("symptom") || qLower.includes("sign") || qLower.includes("spot") || qLower.includes("laksana") || qLower.includes("लक्षण")) {
    const diseaseObj = diseasesList.find(d => diseaseContext && d.disease.toLowerCase().includes(diseaseContext.toLowerCase()));
    if (diseaseObj) {
      return `🔍 Key Symptoms of ${diseaseObj.disease}:\n\n` + diseaseObj.symptoms.map(s => `• ${s}`).join('\n');
    }
    return `Common crop disease symptoms include yellow concentric rings (Early Blight), bright yellow stripe spores (Wheat Rust), spindle-shaped spots (Rice Blast), and sudden vascular wilting (Gram Wilt). Inspect leaf undersides early in the morning.`;
  }

  // General Agronomic Response
  return `🌾 PlantCare AI Assistant (Uttar Pradesh Agriculture):\n\n` +
         `For ${cropContext || "UP crops"} (Wheat, Rice, Sugarcane, Potato, Mustard, Gram, Arhar), always ensure timely sowing, balanced fertilizer application (NPK), and early leaf inspection.\n\n` +
         `How can I assist you further? You can ask about symptoms, cultural management, or verified treatment options.`;
}
