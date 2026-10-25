import hashlib
import hmac
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import streamlit as st
from PIL import Image, ImageOps, UnidentifiedImageError


PROJECT_ROOT = Path(__file__).resolve().parent
ML_SERVICE_DIR = PROJECT_ROOT / "ml-service"
MODEL_PATH = ML_SERVICE_DIR / "models" / "plantvillage_classifier" / "plantvillage_model.pth"
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_MODEL_BYTES = 500 * 1024 * 1024

st.set_page_config(
    page_title="PlantCare AI | Leaf disease detection",
    page_icon="🌿",
    layout="wide",
)


def _setting(name):
    value = os.environ.get(name)
    if value:
        return value

    try:
        return st.secrets.get(name)
    except FileNotFoundError:
        return None


def _download_model():
    model_url = _setting("PLANTVILLAGE_MODEL_URL")
    expected_sha256 = _setting("PLANTVILLAGE_MODEL_SHA256")
    if not model_url:
        return "Model weights are missing. Add the trained model file or configure its URL and SHA-256 in Streamlit secrets."
    if not expected_sha256 or not re.fullmatch(r"[a-fA-F0-9]{64}", expected_sha256):
        return "Set PLANTVILLAGE_MODEL_SHA256 to the model file's 64-character SHA-256 checksum."

    parsed_url = urllib.parse.urlparse(model_url)
    if parsed_url.scheme != "https" or not parsed_url.netloc:
        return "PLANTVILLAGE_MODEL_URL must be a valid HTTPS URL."

    temporary_path = None
    digest = hashlib.sha256()
    bytes_written = 0

    try:
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(model_url, headers={"User-Agent": "PlantCareAI/1.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > MAX_MODEL_BYTES:
                return "The model download exceeds the 500 MB size limit."

            with tempfile.NamedTemporaryFile(
                mode="wb", dir=MODEL_PATH.parent, delete=False
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    bytes_written += len(chunk)
                    if bytes_written > MAX_MODEL_BYTES:
                        return "The model download exceeds the 500 MB size limit."
                    digest.update(chunk)
                    temporary_file.write(chunk)

        if not hmac.compare_digest(digest.hexdigest(), expected_sha256.lower()):
            return "The downloaded model's SHA-256 checksum does not match."

        os.replace(temporary_path, MODEL_PATH)
        temporary_path = None
        return None
    except (OSError, ValueError, urllib.error.URLError) as error:
        return f"Could not download model weights: {error}"
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


@st.cache_resource(show_spinner="Loading the plant disease model...")
def _load_predictor():
    if not MODEL_PATH.is_file():
        download_error = _download_model()
        if download_error:
            return None, download_error

    if str(ML_SERVICE_DIR) not in sys.path:
        sys.path.insert(0, str(ML_SERVICE_DIR))

    from prediction.plantvillage_predictor import pv_predictor_instance

    if not pv_predictor_instance.is_loaded:
        return None, pv_predictor_instance.load_error or "The model could not be loaded."
    return pv_predictor_instance, None


st.markdown(
    """
    <style>
    .block-container {max-width: 1100px; padding-top: 2rem; padding-bottom: 3rem;}
    .hero {padding: 1.6rem 1.8rem; border-radius: 18px; background: #eef7ed; margin-bottom: 1.5rem;}
    .hero p {color: #425344; font-size: 1.05rem; margin-bottom: 0;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>🌿 PlantCare AI</h1>
      <p>Get an AI-assisted plant and leaf disease assessment from a clear photo.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

predictor, model_error = _load_predictor()
with st.sidebar:
    st.subheader("About this tool")
    st.write("Classifies 38 PlantVillage crop and leaf-health categories.")
    st.caption("A clear, well-lit photo of a single leaf usually works best.")
    if predictor:
        st.success("Model ready")
        st.caption(f"Running on {predictor.device}")
    else:
        st.error("Model unavailable")
        st.caption(model_error)
        with st.expander("Configure model weights"):
            st.markdown(
                """
                Add `plantvillage_model.pth` to
                `ml-service/models/plantvillage_classifier/`, or configure these
                Streamlit secrets with a trusted HTTPS model URL:

                ```toml
                PLANTVILLAGE_MODEL_URL = "https://your-host/plantvillage_model.pth"
                PLANTVILLAGE_MODEL_SHA256 = "64-character-file-checksum"
                ```

                Keep `class_names.json` beside the weights. The model URL is only
                downloaded when the model file is absent.
                """
            )

st.subheader("Analyze a leaf")
uploaded_image = st.file_uploader(
    "Upload a leaf image",
    type=["jpg", "jpeg", "png", "webp"],
    help="Supported formats: JPG, PNG, and WEBP. Maximum size: 10 MB.",
)

if uploaded_image:
    image_bytes = uploaded_image.getvalue()
    if len(image_bytes) > MAX_IMAGE_BYTES:
        st.error("This image is larger than 10 MB. Please upload a smaller image.")
    else:
        try:
            with Image.open(uploaded_image) as source_image:
                source_image.load()
                preview = ImageOps.exif_transpose(source_image).convert("RGB").copy()
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
            st.error("This file is not a readable image. Try another JPG, PNG, or WEBP.")
        else:
            image_column, result_column = st.columns([1, 1])
            with image_column:
                st.image(preview, caption="Uploaded leaf", use_container_width=True)
            with result_column:
                st.write("When you are ready, run the analysis.")
                if st.button(
                    "Analyze image",
                    type="primary",
                    use_container_width=True,
                    disabled=predictor is None,
                ):
                    with st.spinner("Analyzing the leaf..."):
                        result = predictor.predict_bytes(image_bytes)

                    if not result.get("success"):
                        st.error(result.get("error", "The image could not be analyzed."))
                    else:
                        st.markdown("### Assessment")
                        crop, disease, confidence = st.columns(3)
                        crop.metric("Plant", result["crop"])
                        disease.metric("Leaf condition", result["disease"])
                        confidence.metric("Confidence", f'{result["confidence_percent"]:.1f}%')

                        if result["prediction_status"] == "low_confidence":
                            st.warning(result["message"])
                        elif result["is_healthy"]:
                            st.success("The model classified this leaf as healthy.")
                        else:
                            st.info("Use this result as a starting point, not a confirmed diagnosis.")

st.divider()
st.caption(
    "PlantCare AI provides AI-assisted guidance only. Confirm serious or spreading "
    "symptoms with a local agricultural extension officer."
)
