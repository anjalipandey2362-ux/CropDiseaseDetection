import axios from 'axios';

const API_BASE_URL = '/api';

/**
 * Sends crop image and location metadata to backend Express API
 */
export async function analyzePlantImageApi(imageFile, selectedDistrict = 'Lucknow', selectedCrop = '') {
  const formData = new FormData();
  formData.append('image', imageFile);
  if (selectedDistrict) formData.append('selectedDistrict', selectedDistrict);
  if (selectedCrop) formData.append('selectedCrop', selectedCrop);

  console.log('[ML] Sending image to prediction API...');

  try {
    const response = await axios.post(`${API_BASE_URL}/analyze-plant`, formData, {
      timeout: 35000
    });

    const resData = response.data;
    if (resData && resData.success) {
      const data = resData.data;
      console.log('[ML] Prediction response:', data);
      console.log('[ML] Crop:', data.crop);
      console.log('[ML] Disease:', data.disease);

      const rawConf = data.confidence !== undefined ? data.confidence : (data.cropConfidence || 0);
      const confPct = data.confidence_percent !== undefined 
        ? data.confidence_percent 
        : (rawConf <= 1.0 ? rawConf * 100 : rawConf);

      console.log('[ML] Confidence:', `${confPct.toFixed(2)}%`);

      return {
        success: true,
        data: data
      };
    } else {
      return {
        success: false,
        error: resData?.error || resData?.message || "AI prediction service is unavailable. Please start the FastAPI ML service."
      };
    }
  } catch (error) {
    console.error('[ML] API call error:', error);
    
    let errorMessage = "Unable to connect to the AI prediction service. Please start the FastAPI ML service.";
    
    if (error.response && error.response.data) {
      const data = error.response.data;
      errorMessage = data.message || data.error || errorMessage;
    } else if (error.code === 'ECONNABORTED') {
      errorMessage = "The AI analysis timed out. Please check your network connection.";
    }

    return {
      success: false,
      error: errorMessage
    };
  }
}

/**
 * Fetch supported crops list
 */
export async function fetchCropsApi() {
  try {
    const response = await axios.get(`${API_BASE_URL}/crops`);
    return response.data.crops || [];
  } catch (err) {
    return [];
  }
}

/**
 * Fetch UP districts list
 */
export async function fetchDistrictsApi() {
  try {
    const response = await axios.get(`${API_BASE_URL}/districts`);
    return response.data.districts || [];
  } catch (err) {
    return [];
  }
}

/**
 * Fetch disease library
 */
export async function fetchDiseaseLibraryApi() {
  try {
    const response = await axios.get(`${API_BASE_URL}/diseases`);
    return response.data.diseases || [];
  } catch (err) {
    return [];
  }
}

/**
 * Fetch weather risk for UP district
 */
export async function fetchWeatherRiskApi(district = 'Lucknow') {
  try {
    const response = await axios.get(`${API_BASE_URL}/weather-risk`, {
      params: { district }
    });
    return response.data;
  } catch (err) {
    return null;
  }
}

/**
 * Ask AI Agronomist Assistant
 */
export async function askAIAssistantApi(question, diseaseContext = "", cropContext = "") {
  try {
    const response = await axios.post(`${API_BASE_URL}/assistant/chat`, {
      question,
      diseaseContext,
      cropContext
    });
    return {
      success: true,
      reply: response.data.reply
    };
  } catch (err) {
    return {
      success: false,
      reply: "Sorry, I am having trouble answering right now. Please consult your local agriculture extension service."
    };
  }
}
