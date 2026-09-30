# 🌿 Crop Disease Detection – PlantCare AI

> **End-to-End Plant Disease Detection Web Application powered by EfficientNet-B0 PyTorch ML Model & 38 PlantVillage Classes.**

PlantCare AI is a full-stack crop disease detection platform. Users upload plant leaf images via the React frontend, which are routed through a Node/Express API server to a Python FastAPI ML service running a pre-trained **EfficientNet-B0** PyTorch model to deliver crop species identification and disease diagnosis.

---

## 🏗️ Project Architecture

```text
React Frontend (Vite, Port 5173)
       │
       │ POST /api/analyze-plant (FormData: image file)
       ▼
Node/Express Backend (Port 5000)
       │
       │ Forward image buffer -> POST http://localhost:8000/predict
       ▼
Python ML Service (FastAPI, Port 8000)
       │
       │ Preprocess: 224x224 RGB, ImageNet normalization
       ▼
EfficientNet-B0 (PyTorch, 38 Classes loaded in memory)
       │
       │ Softmax probabilities & class prediction
       ▼
Prediction Result JSON (crop, disease, confidence %, raw class, status)
       │
       ▼
Node/Express Backend (Resolves verified symptoms & treatments)
       │
       ▼
React UI (Renders ResultCard, Confidence Gauge, PDF Report)
```

---

## 🧠 ML Model Information

- **Model Architecture:** EfficientNet-B0 (`torchvision.models.efficientnet_b0`)
- **Framework:** PyTorch & Torchvision
- **Dataset:** PlantVillage Dataset
- **Number of Classes:** 38
- **Input Dimensions:** 224 x 224 pixels (RGB)
- **Image Normalization:**
  - `mean = [0.485, 0.456, 0.406]`
  - `std  = [0.229, 0.224, 0.225]`
- **Best Validation Accuracy:** **98.35%**
- **Model Files Location:**
  - Weights: `ml-service/models/plantvillage_classifier/plantvillage_model.pth`
  - Class Mapping: `ml-service/models/plantvillage_classifier/class_names.json`
  - Metadata: `ml-service/models/plantvillage_classifier/model_metadata.json`

---

## 📋 38 Supported PlantVillage Classes

1. `Apple___Apple_scab` (Apple Scab)
2. `Apple___Black_rot` (Apple Black Rot)
3. `Apple___Cedar_apple_rust` (Apple Cedar Apple Rust)
4. `Apple___healthy` (Apple Healthy)
5. `Blueberry___healthy` (Blueberry Healthy)
6. `Cherry_(including_sour)___Powdery_mildew` (Cherry Powdery Mildew)
7. `Cherry_(including_sour)___healthy` (Cherry Healthy)
8. `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` (Corn Gray Leaf Spot)
9. `Corn_(maize)___Common_rust_` (Corn Common Rust)
10. `Corn_(maize)___Northern_Leaf_Blight` (Corn Northern Leaf Blight)
11. `Corn_(maize)___healthy` (Corn Healthy)
12. `Grape___Black_rot` (Grape Black Rot)
13. `Grape___Esca_(Black_Measles)` (Grape Esca / Black Measles)
14. `Grape___Leaf_blight_(Isariopsis_Leaf_Spot)` (Grape Leaf Blight)
15. `Grape___healthy` (Grape Healthy)
16. `Orange___Haunglongbing_(Citrus_greening)` (Orange Citrus Greening)
17. `Peach___Bacterial_spot` (Peach Bacterial Spot)
18. `Peach___healthy` (Peach Healthy)
19. `Pepper,_bell___Bacterial_spot` (Pepper Bell Bacterial Spot)
20. `Pepper,_bell___healthy` (Pepper Bell Healthy)
21. `Potato___Early_blight` (Potato Early Blight)
22. `Potato___Late_blight` (Potato Late Blight)
23. `Potato___healthy` (Potato Healthy)
24. `Raspberry___healthy` (Raspberry Healthy)
25. `Soybean___healthy` (Soybean Healthy)
26. `Squash___Powdery_mildew` (Squash Powdery Mildew)
27. `Strawberry___Leaf_scorch` (Strawberry Leaf Scorch)
28. `Strawberry___healthy` (Strawberry Healthy)
29. `Tomato___Bacterial_spot` (Tomato Bacterial Spot)
30. `Tomato___Early_blight` (Tomato Early Blight)
31. `Tomato___Late_blight` (Tomato Late Blight)
32. `Tomato___Leaf_Mold` (Tomato Leaf Mold)
33. `Tomato___Septoria_leaf_spot` (Tomato Septoria Leaf Spot)
34. `Tomato___Spider_mites Two-spotted_spider_mite` (Tomato Spider Mites)
35. `Tomato___Target_Spot` (Tomato Target Spot)
36. `Tomato___Tomato_Yellow_Leaf_Curl_Virus` (Tomato Yellow Leaf Curl Virus)
37. `Tomato___Tomato_mosaic_virus` (Tomato Mosaic Virus)
38. `Tomato___healthy` (Tomato Healthy)

---

## ⚙️ Environment Variables

### Backend (`backend/.env`):
```env
PORT=5000
ML_SERVICE_URL=http://localhost:8000
CONFIDENCE_THRESHOLD=0.60
```

---

## 🛠️ Installation & Setup

### 1. Python ML Service Setup
```bash
cd ml-service
pip install -r requirements.txt
```

### 2. Node Backend Setup
```bash
cd backend
npm install
```

### 3. React Frontend Setup
```bash
cd frontend
npm install
```

---

## 🚀 How to Run the Application

Start the three services in separate terminals:

### Step 1: Start Python ML Service (FastAPI)
```bash
# From project root
python ml-service/main.py
```
*Runs on `http://localhost:8000` and pre-loads `plantvillage_model.pth` into memory ONCE.*

### Step 2: Start Node/Express Backend
```bash
cd backend
npm start
```
*Runs on `http://localhost:5000`.*

### Step 3: Start React Frontend
```bash
cd frontend
npm run dev
```
*Runs on `http://localhost:5173`.*

---

## 🔌 API Endpoints & Example Responses

### Python ML Endpoint
`POST http://localhost:8000/predict`
- **Body:** `multipart/form-data` with field `file` or `image`

#### Example Response (`200 OK`):
```json
{
  "success": true,
  "prediction_status": "success",
  "crop": "Tomato",
  "disease": "Late Blight",
  "confidence": 0.9842,
  "confidence_percent": 98.42,
  "raw_class_name": "Tomato___Late_blight",
  "class_index": 30,
  "is_healthy": false,
  "message": null
}
```

#### Low Confidence Response (`confidence < 0.60`):
```json
{
  "success": true,
  "prediction_status": "low_confidence",
  "crop": "Tomato",
  "disease": "Uncertain",
  "confidence": 0.4521,
  "confidence_percent": 45.21,
  "raw_class_name": "Tomato___Late_blight",
  "class_index": 30,
  "is_healthy": false,
  "message": "The image could not be classified confidently. Please upload a clear image of the affected leaf."
}
```

### Node/Express Backend Endpoint
`POST http://localhost:5000/api/analyze-plant`
- **Body:** `multipart/form-data` with field `image`

---

## 🧪 Testing Instructions

### Test Python ML Inference Unit Test:
```bash
python ml-service/test_inference.py
```

### Test End-to-End Pipeline (Node -> Python ML -> EfficientNet-B0):
```bash
node scratch/test_e2e_pipeline.js
```

---

## ⚠️ Agricultural Disclaimer

> **PlantCare AI provides AI-assisted decision support and agricultural extension information. Image predictions should be verified with local agricultural extension officers when severe symptoms occur.**
