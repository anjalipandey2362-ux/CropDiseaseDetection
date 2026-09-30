import io
from PIL import Image

try:
    import torchvision.transforms as transforms
    HAS_TORCHVISION = True
except ImportError:
    HAS_TORCHVISION = False

def preprocess_image(image_bytes: bytes):
    """
    Preprocesses uploaded raw image bytes for EfficientNet-B0 inference.
    Resizes image to 224x224 and applies ImageNet normalization.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    if HAS_TORCHVISION:
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        tensor = transform(image).unsqueeze(0) // Batch size 1
        return tensor
    
    return image
