import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { predictCropAndDisease } from '../services/modelService.js';
import { getVerifiedTreatmentAndDetails, getAllVerifiedTreatments } from '../services/treatmentService.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const cropsList = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/crops.json'), 'utf8'));
const diseasesList = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/diseases.json'), 'utf8'));
const districtsList = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/districts.json'), 'utf8'));

/**
 * Handles image upload and coordinates prediction through Python FastAPI ML service
 * and verified treatment database retrieval.
 */
export async function analyzePlant(req, res) {
  try {
    // 1. File validation
    if (!req.file) {
      return res.status(400).json({
        error: "Missing image file",
        message: "Please upload a clear image where the affected crop leaf is visible."
      });
    }

    const { mimetype, size, originalname, buffer } = req.file;

    // Format validation
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(mimetype.toLowerCase())) {
      return res.status(400).json({
        error: "Unsupported image format",
        message: "Only JPG, JPEG, PNG, and WebP image formats are supported."
      });
    }

    // Size limit (10MB)
    const MAX_SIZE = 10 * 1024 * 1024;
    if (size > MAX_SIZE) {
      return res.status(400).json({
        error: "Image file too large",
        message: "Image file size exceeds 10MB limit. Please upload a smaller image."
      });
    }

    const selectedCrop = req.body.selectedCrop || null;
    const selectedDistrict = req.body.selectedDistrict || "Lucknow";

    // 2. Perform ML Prediction via modelService (Express -> FastAPI -> EfficientNet-B0)
    const prediction = await predictCropAndDisease(buffer, originalname, selectedCrop);

    if (!prediction || prediction.status === 'error' || prediction.error) {
      return res.status(503).json({
        success: false,
        error: prediction?.error || "AI prediction service is unavailable. Please start the FastAPI ML service.",
        message: prediction?.error || "AI prediction service is unavailable. Please start the FastAPI ML service."
      });
    }

    // 3. Fetch verified treatment details and enforce low confidence protection
    const fullAnalysisResult = getVerifiedTreatmentAndDetails(prediction, { selectedDistrict });

    return res.status(200).json({
      success: true,
      data: {
        ...fullAnalysisResult,
        district: selectedDistrict,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    console.error("[PlantController] Error analyzing plant image:", error);
    return res.status(500).json({
      error: "Analysis Failed",
      message: "An unexpected error occurred while processing the crop leaf image. Please try again."
    });
  }
}

/**
 * Returns list of supported crops for UP
 */
export async function getCrops(req, res) {
  return res.status(200).json({ crops: cropsList });
}

/**
 * Returns disease library list
 */
export async function getDiseases(req, res) {
  return res.status(200).json({ diseases: diseasesList });
}

/**
 * Returns list of districts in Uttar Pradesh
 */
export async function getDistricts(req, res) {
  return res.status(200).json({ districts: districtsList });
}

/**
 * Returns list of verified treatments
 */
export async function getTreatments(req, res) {
  return res.status(200).json({ treatments: getAllVerifiedTreatments() });
}

/**
 * Returns simulated weather disease risk assessment for UP districts
 */
export async function getWeatherRisk(req, res) {
  const district = req.query.district || "Lucknow";
  
  // Seasonal weather risk context for UP (Dec-Feb is cool/foggy; Jul-Sep is humid monsoonal)
  const currentMonth = new Date().getMonth(); // 0-11
  let riskLevel = "Moderate";
  let highRiskDiseases = [];
  let temp = "24°C";
  let humidity = "78%";
  let forecastMessage = "";

  if (currentMonth === 11 || currentMonth === 0 || currentMonth === 1) { // Winter (Dec, Jan, Feb)
    riskLevel = "High";
    highRiskDiseases = ["Wheat Yellow Rust", "Potato Late Blight", "Mustard Alternaria Blight"];
    temp = "16°C";
    humidity = "88%";
    forecastMessage = "High humidity and morning fog create critical conditions for Yellow Rust and Late Blight spread in UP plains.";
  } else if (currentMonth >= 6 && currentMonth <= 8) { // Monsoon (Jul, Aug, Sep)
    riskLevel = "High";
    highRiskDiseases = ["Rice Blast", "Sugarcane Red Rot", "Maize Blight"];
    temp = "31°C";
    humidity = "84%";
    forecastMessage = "Warm temperatures and monsoonal rainfall accelerate fungal spore germination in paddy and sugarcane fields.";
  } else {
    riskLevel = "Low";
    highRiskDiseases = ["Chickpea Fusarium Wilt"];
    temp = "28°C";
    humidity = "62%";
    forecastMessage = "Moderate temperature and dry conditions reduce active leaf disease risk. Continue routine field monitoring.";
  }

  return res.status(200).json({
    district: district,
    temperature: temp,
    humidity: humidity,
    riskLevel: riskLevel,
    highRiskDiseases: highRiskDiseases,
    forecastMessage: forecastMessage,
    disclaimer: "Weather indicators provide crop disease risk context only and do not confirm disease presence in specific fields."
  });
}
