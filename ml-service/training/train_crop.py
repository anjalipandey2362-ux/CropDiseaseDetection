"""
PlantVillage Baseline Classifier (plantvillage_classifier) Training Script

ARCHITECTURE & STAGING NOTE:
--------------------------------------
This file reframes the PlantVillage 38-class dataset model as `plantvillage_classifier`.
It is a 38-class PlantVillage crop+disease baseline model.

TODO:
The final Stage-1 crop classifier must be trained separately using crop-level labels
(e.g., wheat, rice, sugarcane, potato, maize, mustard, chickpea, pigeon_pea, lentil, pea).
Do NOT use this 38-class PlantVillage baseline model as the production Stage-1 crop classifier.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training.train_plantvillage import train_plantvillage_classifier, main

if __name__ == "__main__":
    main()
