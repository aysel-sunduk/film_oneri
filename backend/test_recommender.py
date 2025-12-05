# backend/test_recommender.py

from backend.services.recommender_service import MODEL_DIR, BINARIZER_PATH
import os, joblib
from autogluon.tabular import TabularPredictor

print("MODEL_DIR:", MODEL_DIR)
print("BINARIZER_PATH:", BINARIZER_PATH)

# 1) Binarizer'ı test et
print(">>> Binarizer yükleniyor...")
mlb = joblib.load(BINARIZER_PATH)
print("OK, target_labels:", list(mlb.classes_))

# 2) Bir tane predictor'u test et (ör: mutlu)
predictor_path = os.path.join(MODEL_DIR, "predictor_mutlu")
print(">>> Predictor yükleniyor:", predictor_path)
predictor = TabularPredictor.load(predictor_path)
print("Predictor OK:", predictor)