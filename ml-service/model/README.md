# Model Storage Directory

Place your trained PyTorch model weights file here named:
`crop_disease_model.pth`

When `crop_disease_model.pth` is present in this directory, the FastAPI ML service automatically loads the trained EfficientNet-B0 PyTorch model for real predictions.

If this file is absent, the ML service automatically runs in clearly marked **Development Mode** for UI testing.
