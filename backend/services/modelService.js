import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const diseasesDataPath = path.join(__dirname, '../data/diseases.json');
const cropsDataPath = path.join(__dirname, '../data/crops.json');
const supportedCropsPath = path.join(__dirname, '../data/supportedCrops.json');

const diseasesList = JSON.parse(fs.readFileSync(diseasesDataPath, 'utf8'));
const cropsList = JSON.parse(fs.readFileSync(cropsDataPath, 'utf8'));
const supportedCropsConfig = JSON.parse(fs.readFileSync(supportedCropsPath, 'utf8'));

export async function predictCropAndDisease(imageBuffer, filename = 'leaf.jpg', selectedCrop = null) {
  const mlServiceUrl = process.env.ML_SERVICE_URL || 'http://127.0.0.1:8000';

  console.log(`[ML] Sending image to prediction API at ${mlServiceUrl}/predict...`);

  try {
    const formData = new FormData();
    formData.append('image', imageBuffer, {
      filename: filename,
      contentType: 'image/jpeg'
    });

    const response = await axios.post(`${mlServiceUrl}/predict`, formData, {
      headers: formData.getHeaders(),
      timeout: 20000
    });

    const data = response.data;
    console.log('[ML] Prediction response:', data);

    if (data) {
      if (data.success === false) {
        return {
          status: 'error',
          error: data.error || 'AI prediction service is unavailable. Please start the FastAPI ML service.'
        };
      }

      // Raw confidence parsing (support decimal like 0.9994 and percentage like 99.94)
      const rawConf = data.confidence !== undefined 
        ? data.confidence 
        : (data.crop_confidence !== undefined ? data.crop_confidence : 0.0);

      let confDecimal = 0.0;
      let confPercent = 0.0;

      if (data.confidence_percent !== undefined) {
        confPercent = Number(data.confidence_percent);
        confDecimal = confPercent > 1.0 ? confPercent / 100.0 : confPercent;
      } else if (rawConf > 1.0) {
        confPercent = rawConf;
        confDecimal = rawConf / 100.0;
      } else {
        confDecimal = rawConf;
        confPercent = rawConf * 100.0;
      }

      confPercent = Math.round(confPercent * 100) / 100;
      confDecimal = Math.round(confDecimal * 10000) / 10000;

      const isLowConfidence = data.prediction_status === 'low_confidence' || confDecimal < 0.60;

      const cropName = data.crop || null;
      const diseaseName = data.disease || null;

      console.log('[ML] Crop:', cropName);
      console.log('[ML] Disease:', diseaseName);
      console.log('[ML] Confidence:', `${confPercent}%`);

      return {
        status: isLowConfidence ? 'uncertain_disease' : 'success',
        prediction_status: data.prediction_status || (isLowConfidence ? 'low_confidence' : 'success'),
        crop: cropName,
        cropConfidence: confDecimal,
        disease: diseaseName,
        diseaseConfidence: confDecimal,
        confidence: confDecimal,
        confidence_percent: confPercent,
        raw_class_name: data.raw_class_name || data.class_name || null,
        class_index: data.class_index !== undefined ? data.class_index : null,
        is_healthy: Boolean(data.is_healthy),
        message: data.message || (isLowConfidence ? "The image could not be classified confidently. Please upload a clear image of the affected leaf." : null),
        supportedCrops: data.supportedCrops || [],
        topPredictions: data.topPredictions || [],
        isDevMode: false,
        debug: data.debug || null
      };
    }
  } catch (err) {
    console.error(`[ML] Python FastAPI ML service unreachable at ${mlServiceUrl}:`, err.message);
    return {
      status: 'error',
      error: "AI prediction service is unavailable. Please start the FastAPI ML service."
    };
  }

  return {
    status: 'error',
    error: "AI prediction service is unavailable. Please start the FastAPI ML service."
  };
}

/**
 * Local Fallback Predictor for offline development mode.
 * NEVER forces unlabelled images to Wheat or Sugarcane!
 */
function fallbackSimulatedPredictor(buffer, filename, selectedCrop) {
  const fnLower = filename.toLowerCase();

  let matchedCrop = null;
  let matchedDisease = null;
  let isUnsupported = false;
  let isNonPlant = false;

  // Keyword-based recognition in dev fallback mode
  if (fnLower.includes('apple') || fnLower.includes('seb')) {
    matchedCrop = "Apple";
    isUnsupported = true;
  } else if (fnLower.includes('tomato') || fnLower.includes('tamatar')) {
    matchedCrop = "Tomato";
    isUnsupported = true;
  } else if (fnLower.includes('car') || fnLower.includes('shoe') || fnLower.includes('non_plant') || fnLower.includes('object')) {
    isNonPlant = true;
  } else if (fnLower.includes('wheat') || fnLower.includes('gehu')) {
    matchedCrop = "Wheat";
    matchedDisease = diseasesList.find(d => d.id === 'wheat_stripe_rust');
  } else if (fnLower.includes('sugarcane') || fnLower.includes('ganna')) {
    matchedCrop = "Sugarcane";
    matchedDisease = diseasesList.find(d => d.id === 'sugarcane_red_rot');
  } else if (fnLower.includes('potato') || fnLower.includes('aalu')) {
    matchedCrop = "Potato";
    matchedDisease = diseasesList.find(d => d.id === 'potato_late_blight');
  } else if (fnLower.includes('rice') || fnLower.includes('paddy') || fnLower.includes('dhan')) {
    matchedCrop = "Rice / Paddy";
    matchedDisease = diseasesList.find(d => d.id === 'rice_blast');
  } else if (fnLower.includes('maize') || fnLower.includes('corn')) {
    matchedCrop = "Maize";
    matchedDisease = diseasesList.find(d => d.id === 'maize_maydis_blight');
  } else if (selectedCrop) {
    matchedCrop = selectedCrop;
    const cropDiseases = diseasesList.filter(d => d.crop.toLowerCase() === selectedCrop.toLowerCase());
    if (cropDiseases.length > 0) matchedDisease = cropDiseases[0];
  }

  const supportedCropNames = supportedCropsConfig.supportedDiseaseCrops.map(c => c.name);

  // State D — Non-plant
  if (isNonPlant) {
    return {
      status: "non_plant",
      crop: null,
      cropConfidence: 0.85,
      disease: null,
      diseaseConfidence: 0.0,
      message: "⚠️ No supported plant/crop detected. Please upload a clear image of an agricultural crop.",
      supportedCrops: supportedCropNames,
      topPredictions: [{ crop: "Non-plant", confidence: 0.85 }, { crop: "Unknown", confidence: 0.10 }],
      isDevMode: true
    };
  }

  // State B — Unsupported Crop (e.g. Apple)
  if (isUnsupported && matchedCrop) {
    return {
      status: "unsupported_crop",
      crop: matchedCrop,
      cropConfidence: 0.91,
      disease: null,
      diseaseConfidence: 0.0,
      message: `🍎 ${matchedCrop} detected. This crop is currently outside the supported agricultural disease-detection model.`,
      supportedCrops: supportedCropNames,
      topPredictions: [{ crop: matchedCrop, confidence: 0.91 }, { crop: "Unknown", confidence: 0.05 }],
      isDevMode: true,
      debug: {
        crop_prediction: matchedCrop,
        crop_confidence: 0.91,
        status: "STOPPED (UNSUPPORTED CROP)"
      }
    };
  }

  // State C — Unknown Crop (when filename has no crop keyword & user didn't select crop)
  if (!matchedCrop || !matchedDisease) {
    return {
      status: "uncertain_crop",
      crop: null,
      cropConfidence: 0.42,
      disease: null,
      diseaseConfidence: 0.0,
      message: "⚠️ Crop could not be identified confidently. Please upload a clear crop image.",
      supportedCrops: supportedCropNames,
      topPredictions: [{ crop: "Unknown", confidence: 0.42 }, { crop: "Wheat", confidence: 0.08 }],
      isDevMode: true,
      debug: {
        crop_prediction: "Unknown",
        crop_confidence: 0.42,
        status: "STOPPED (UNCERTAIN CROP)"
      }
    };
  }

  // State A — Supported Crop & Disease Success
  return {
    status: "success",
    crop: matchedCrop,
    cropConfidence: 0.94,
    disease: matchedDisease.disease,
    diseaseConfidence: 0.91,
    supportedCrops: supportedCropNames,
    topPredictions: [{ crop: matchedCrop, confidence: 0.94 }, { crop: "Maize", confidence: 0.04 }],
    isDevMode: true,
    debug: {
      crop_prediction: matchedCrop,
      crop_confidence: 0.94,
      disease_prediction: matchedDisease.disease,
      disease_confidence: 0.91,
      crop_model: "models/crop_classifier/crop_model.pth (Dev Mode)",
      disease_model: `models/${matchedCrop.toLowerCase().split(' ')[0]}/disease_model.pth (Dev Mode)`,
      consistency_check: "PASSED"
    }
  };
}
