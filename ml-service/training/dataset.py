import os
from PIL import Image

try:
    import torch
    from torch.utils.data import Dataset
    import torchvision.transforms as transforms
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

class CropDiseaseDataset(Dataset if HAS_TORCH else object):
    """
    PyTorch Dataset for agricultural crop disease images stored in:
    dataset/
      ├── wheat/
      │   ├── healthy/
      │   ├── rust/
      │   └── other_disease/
      ├── rice/
      │   ├── healthy/
      │   ├── blast/
      │   └── bacterial_blight/
      ...
    """
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.samples = []
        self.classes = []
        self._load_dataset()

    def _load_dataset(self):
        if not os.path.exists(self.root_dir):
            print(f"Directory {self.root_dir} does not exist.")
            return

        class_set = set()
        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    rel_path = os.path.relpath(root, self.root_dir)
                    class_name = rel_path.replace(os.path.sep, "_")
                    class_set.add(class_name)
                    self.samples.append((os.path.join(root, file), class_name))

        self.classes = sorted(list(class_set))
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, class_name = self.samples[idx]
        image = Image.open(path).convert('RGB')
        label = self.class_to_idx[class_name]

        if self.transform:
            image = self.transform(image)

        return image, label
