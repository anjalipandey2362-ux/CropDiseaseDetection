import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import plantRoutes from './routes/plantRoutes.js';
import assistantRoutes from './routes/assistantRoutes.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// CORS setup to allow requests from Vite dev server or frontend client
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Register routes
app.use('/api', plantRoutes);
app.use('/api/assistant', assistantRoutes);
// Legacy compatibility route
app.use('/api/chat', assistantRoutes);

// Root route
app.get('/', (req, res) => {
  res.send({
    app: "PlantCare AI Backend API (Uttar Pradesh Agriculture Focus)",
    status: "Active",
    mlServiceUrl: process.env.ML_SERVICE_URL || "http://localhost:8000",
    confidenceThreshold: process.env.CONFIDENCE_THRESHOLD || "0.70",
    endpoints: [
      "POST /api/analyze-plant",
      "GET /api/crops",
      "GET /api/diseases",
      "GET /api/districts",
      "GET /api/treatments",
      "GET /api/weather-risk",
      "POST /api/assistant/chat"
    ]
  });
});

app.listen(PORT, () => {
  console.log(`=======================================================`);
  console.log(`🌾 PlantCare AI Backend Server running on port ${PORT}`);
  console.log(`📍 Focus: Uttar Pradesh Crop Disease Detection`);
  console.log(`🔗 Endpoint: http://localhost:${PORT}/api/analyze-plant`);
  console.log(`🤖 ML Service Target: ${process.env.ML_SERVICE_URL || 'http://localhost:8000'}`);
  console.log(`=======================================================`);
});
