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
 * STRICT CROP + DISEASE TREATMENT LOOKUP
 * getTreatment(crop, disease)
 * Never returns treatment based on disease name alone!
 */
export function getTreatment(cropName, diseaseName) {
  if (!cropName || !diseaseName) return null;

  return treatmentsList.find(t => 
    t.crop.toLowerCase() === cropName.toLowerCase() &&
    (t.disease.toLowerCase().includes(diseaseName.toLowerCase().split(' ')[0]) || 
     diseaseName.toLowerCase().includes(t.disease.toLowerCase().split(' ')[0]))
  ) || null;
}

/**
 * Coordinates disease info and verified treatment lookup across 5 Result States.
 */
export function getVerifiedTreatmentAndDetails(prediction, options = {}) {
  const { 
    status = 'success', 
    crop, 
    cropConfidence = 0.90, 
    disease, 
    diseaseConfidence = 0.90, 
    isDevMode, 
    debug,
    message,
    supportedCrops = [],
    topPredictions = []
  } = prediction;

  const CONFIDENCE_THRESHOLD = parseFloat(process.env.CONFIDENCE_THRESHOLD || 0.70);

  // STATE B: Unsupported Crop (e.g. Apple, Tomato)
  if (status === 'unsupported_crop') {
    return {
      status: 'unsupported_crop',
      crop: crop || "Unsupported Crop",
      cropConfidence: cropConfidence,
      disease: null,
      diseaseConfidence: 0.0,
      confidence: cropConfidence,
      isLowConfidence: false,
      severity: "Not available",
      message: message || `🍎 ${crop} detected. This crop is currently outside the supported agricultural disease-detection model.`,
      supportedCrops: supportedCrops,
      symptoms: [],
      symptomsHindi: [],
      verifiedTreatment: null,
      treatmentMessage: `Treatment recommendations are not available for ${crop} as it is outside the supported crop models.`,
      culturalManagement: [],
      prevention: [],
      topPredictions: topPredictions,
      isDevMode: isDevMode,
      debug: debug
    };
  }

  // STATE D: Non-plant Image
  if (status === 'non_plant') {
    return {
      status: 'non_plant',
      crop: "No Plant Detected",
      cropConfidence: cropConfidence,
      disease: null,
      diseaseConfidence: 0.0,
      confidence: cropConfidence,
      isLowConfidence: true,
      severity: "Not available",
      message: message || "⚠️ No supported plant/crop detected. Please upload a clear image of an agricultural crop.",
      supportedCrops: supportedCrops,
      symptoms: [],
      symptomsHindi: [],
      verifiedTreatment: null,
      treatmentMessage: null,
      culturalManagement: [],
      prevention: [],
      topPredictions: topPredictions,
      isDevMode: isDevMode,
      debug: debug
    };
  }

  // STATE C: Uncertain Crop
  if (status === 'uncertain_crop' || !crop || cropConfidence < CONFIDENCE_THRESHOLD) {
    return {
      status: 'uncertain_crop',
      crop: "Crop Identification Uncertain",
      cropConfidence: cropConfidence,
      disease: null,
      diseaseConfidence: 0.0,
      confidence: cropConfidence,
      isLowConfidence: true,
      severity: "Not available",
      message: message || "The image could not be classified confidently. Please upload a clear image of the affected leaf.",
      supportedCrops: supportedCrops,
      symptoms: [],
      symptomsHindi: [],
      verifiedTreatment: null,
      treatmentMessage: null,
      culturalManagement: ["Ensure the leaf photo is taken in daylight with spots clearly visible."],
      prevention: [],
      topPredictions: topPredictions,
      isDevMode: isDevMode,
      debug: debug
    };
  }

  // STATE E: Low Disease Confidence
  if (status === 'uncertain_disease' || status === 'low_confidence' || !disease || diseaseConfidence < CONFIDENCE_THRESHOLD) {
    return {
      status: 'uncertain_disease',
      crop: crop,
      cropConfidence: cropConfidence,
      disease: "Disease Identification Uncertain",
      diseaseConfidence: diseaseConfidence,
      confidence: diseaseConfidence,
      isLowConfidence: true,
      severity: "Not available",
      message: message || "The image could not be classified confidently. Please upload a clear image of the affected leaf.",
      supportedCrops: supportedCrops,
      symptoms: [],
      symptomsHindi: [],
      verifiedTreatment: null,
      treatmentMessage: "No specific chemical treatment is provided for low-confidence disease predictions.",
      culturalManagement: ["Monitor leaf foliage closely for expanding spots."],
      prevention: [],
      topPredictions: topPredictions,
      isDevMode: isDevMode,
      debug: debug
    };
  }

  // STATE A: Supported Crop & Disease Success
  const diseaseInfo = diseasesList.find(d => 
    d.crop.toLowerCase() === crop.toLowerCase() && 
    (disease.toLowerCase().includes(d.disease.toLowerCase().split(' ')[0]) || d.disease.toLowerCase().includes(disease.toLowerCase().split(' ')[0]))
  );

  // Strict Treatment Lookup using BOTH crop AND disease: getTreatment(crop, disease)
  const verifiedTreatment = getTreatment(crop, disease);

  return {
    status: 'success',
    crop: crop,
    cropHindi: diseaseInfo ? diseaseInfo.cropHindi : crop,
    cropConfidence: cropConfidence,
    disease: diseaseInfo ? diseaseInfo.disease : disease,
    diseaseHindi: diseaseInfo ? diseaseInfo.diseaseHindi : disease,
    diseaseConfidence: diseaseConfidence,
    confidence: Math.min(cropConfidence, diseaseConfidence),
    isLowConfidence: false,
    severity: diseaseInfo ? diseaseInfo.severity : "Moderate",
    symptoms: diseaseInfo ? diseaseInfo.symptoms : [],
    symptomsHindi: diseaseInfo ? diseaseInfo.symptomsHindi : [],
    verifiedTreatment: verifiedTreatment ? {
      activeIngredient: verifiedTreatment.activeIngredient,
      productName: verifiedTreatment.productName,
      treatmentType: verifiedTreatment.treatmentType,
      applicationGuidance: verifiedTreatment.applicationGuidance,
      safetyInformation: verifiedTreatment.safetyInformation,
      biologicalTreatment: verifiedTreatment.biologicalTreatment,
      source: verifiedTreatment.source,
      lastVerified: verifiedTreatment.lastVerified
    } : null,
    treatmentMessage: verifiedTreatment ? null : "Treatment information not available.",
    culturalManagement: diseaseInfo ? diseaseInfo.culturalManagement : (verifiedTreatment ? [verifiedTreatment.culturalManagement] : []),
    prevention: diseaseInfo ? diseaseInfo.prevention : [],
    topPredictions: topPredictions,
    isDevMode: isDevMode,
    debug: debug
  };
}

export function getAllVerifiedTreatments() {
  return treatmentsList;
}
