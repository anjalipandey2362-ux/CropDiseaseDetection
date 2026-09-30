# Agricultural Crop Disease Dataset Directory

Organize your training image dataset in the following folder structure:

```text
dataset/
│
├── wheat/
│   ├── healthy/
│   ├── stripe_rust/
│   └── leaf_rust/
│
├── rice/
│   ├── healthy/
│   ├── blast/
│   └── bacterial_blight/
│
├── sugarcane/
│   ├── healthy/
│   └── red_rot/
│
├── potato/
│   ├── healthy/
│   ├── early_blight/
│   └── late_blight/
│
├── maize/
│   ├── healthy/
│   └── maydis_blight/
│
├── mustard/
│   ├── healthy/
│   └── alternaria_blight/
│
├── chickpea/
│   ├── healthy/
│   └── fusarium_wilt/
│
└── pigeon_pea/
    ├── healthy/
    └── fusarium_wilt/
```

After placing images in these folders, run the PyTorch training script:
`python ml-service/training/train.py --data_dir dataset`
