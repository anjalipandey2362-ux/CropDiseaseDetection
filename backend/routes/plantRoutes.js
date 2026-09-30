import express from 'express';
import multer from 'multer';
import { 
  analyzePlant, 
  getCrops, 
  getDiseases, 
  getDistricts, 
  getTreatments, 
  getWeatherRisk 
} from '../controllers/plantController.js';

const router = express.Router();

// Configure multer memory storage
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 } // 10MB limit
});

// Image analysis route
router.post('/analyze-plant', upload.single('image'), analyzePlant);

// Data routes
router.get('/crops', getCrops);
router.get('/diseases', getDiseases);
router.get('/districts', getDistricts);
router.get('/treatments', getTreatments);
router.get('/weather-risk', getWeatherRisk);

export default router;
