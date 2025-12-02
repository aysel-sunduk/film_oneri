"""
Veritabanındaki filmleri ve atanan duygu etiketlerini kullanarak 
AutoGluon ile Çoklu Etiket Sınıflandırma modelini eğiten script.
"""

import sys
import os
import pandas as pd
from typing import Optional, List
import joblib
from sklearn.model_selection import train_test_split

# AutoGluon import'ları (aynı kalır)
try:
    from autogluon.tabular import TabularPredictor
    from sklearn.preprocessing import MultiLabelBinarizer
    from sklearn.metrics import accuracy_score, f1_score
    ML_LIBRARIES_AVAILABLE = True
except ImportError:
    ML_LIBRARIES_AVAILABLE = False
    print("⚠️ Gerekli kütüphaneler eksik. Lütfen kurun: pip install autogluon scikit-learn")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.connection import get_db_session
from backend.db.models import Movie, Emotion
from backend.config import settings

# --- GLOBAL AYARLAR VE KLASÖR KONTROLÜ (Aynı Kalır) ---
if ML_LIBRARIES_AVAILABLE:
    MODEL_DIR = os.path.dirname(settings.BEST_MODEL_PATH)
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR, exist_ok=True)
        print(f"📁 Model klasörü oluşturuldu: {MODEL_DIR}")
# ------------------------------------------------------


def prepare_data_for_autogluon() -> Optional[pd.DataFrame]:
    """Veritabanından etiketli veriyi çeker ve binarize eder."""
    # (Bu fonksiyonun içeriği değişmedi)
    # ... (önceki kod)
    
    # Kodu önceki cevabınızdan kopyalayın
    print("1. Veritabanından etiketli veriler çekiliyor...")
    session = get_db_session()
    
    try:
        results = session.query(Movie, Emotion).join(
            Emotion, Movie.movie_id == Emotion.movie_id
        ).all()
        
        if not results:
            print("❌ Eğitim için etiketli veri bulunamadı.")
            return None
        
        data = []
        for movie, emotion in results:
            data.append({
                'movie_id': movie.movie_id,
                'overview': movie.overview,
                'emotion_label': emotion.emotion_label
            })
        
        df = pd.DataFrame(data)
        df_grouped = df.groupby('movie_id').agg({
            'overview': 'first',
            'emotion_label': lambda x: list(x)
        }).reset_index()
        
        df_grouped = df_grouped[df_grouped['overview'].str.strip() != '']
        print(f"✅ Çekilen ve temizlenen film sayısı: {len(df_grouped)}")
        
        mlb = MultiLabelBinarizer()
        mlb.fit([settings.EMOTION_CATEGORIES]) 
        
        y_multi_hot = mlb.transform(df_grouped['emotion_label'])
        df_labels = pd.DataFrame(y_multi_hot, columns=mlb.classes_)
        df_train = pd.concat([df_grouped.drop(columns=['emotion_label']), df_labels], axis=1)
        
        df_train['overview'] = df_train['overview'].fillna('').astype(str)
        
        mlb_path = os.path.join(MODEL_DIR, "multi_label_binarizer.pkl")
        joblib.dump(mlb, mlb_path)
        print(f"✅ MultiLabelBinarizer kaydedildi: {mlb_path}")

        return df_train

    except Exception as e:
        print(f"❌ Veri hazırlama hatası: {e}")
        return None
    finally:
        session.close()


def train_autogluon_model(df_train: pd.DataFrame, target_labels: List[str]):
    """
    Veriyi ayırır, Ray'i devre dışı bırakarak AutoGluon modelini eğitir ve performansını ölçer.
    """
    if not ML_LIBRARIES_AVAILABLE:
        return

    print("\n3. 🔍 Veri, Eğitim ve Test Setlerine Ayrılıyor (Overfitting azaltma)...")
    
    # Aşırı öğrenmeyi kontrol etmek için veriyi eğitim ve test setlerine ayır
    df_train_set, df_test_set = train_test_split(
        df_train, 
        test_size=0.20, 
        random_state=42,
        shuffle=True
    )
    
    print(f"   Eğitim Seti Boyutu: {len(df_train_set)} film")
    print(f"   Test Seti Boyutu: {len(df_test_set)} film")


    print("\n4. 🤖 AutoGluon Modeli Eğitiliyor (Çoklu Etiket Sınıflandırma)...")
    print("   ✅ Paralel işlemciler azaltıldı (num_cpus=0.5).")
    
    # 5. Model Değerlendirme için sonuçları tutacak dictionary
    results = {}
    
    for i, label in enumerate(target_labels):
        print(f"\n--- Eğitiliyor: {label} ({i+1}/{len(target_labels)}) ---")
        
        predictor = TabularPredictor(
            label=label, 
            path=os.path.join(MODEL_DIR, f'predictor_{label}'),
            eval_metric='f1_macro' 
        ).fit(
            train_data=df_train_set[['overview'] + target_labels], 
            time_limit=3600, # Süreyi 1 saate çıkarıldı
            presets='best_quality', 

            dynamic_stacking=False, # DyStack'i kapatır
            num_stack_levels=0,      # Sadece temel (L1) modelleri eğitir, Ray'i kullanan Stacking'i minimize eder.
            # RAY/ÇOKLU İŞLEMCİ sorununu çözen parametreler:
            ag_args_fit={'num_cpus': 1}, # Ray'i devre dışı bırakır, kararlılığı artırır 
            ag_args_ensemble={'num_folds': 4, 'num_cpus': 1}, # Fold sayısını düşürerek hafıza sorununu azaltır
            # Aşırı öğrenmeyi azaltmak için early stopping sıkılaştırılabilir:
            hyperparameters='default', # Hyperparametre tuning'i varsayılan hale getirir.
        )
        
        # 5. Model Değerlendirme (Gerçek Genelleme Yeteneği)
        
        # Test seti üzerinde tahmin yap
        y_true = df_test_set[label]
        y_pred = predictor.predict(df_test_set)
        
        # F1 ve Doğruluk (Accuracy) Hesapla
        acc = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)
        
        results[label] = {
            "best_f1_score": f1,
            "accuracy_score": acc,
            "best_model": predictor.info()['best_model']
        }
        
        print(f"✅ {label} Sonuç (Test Seti Üzerinde):")
        print(f"   En iyi model: {results[label]['best_model']}")
        print(f"   Test Acc: {acc:.4f} | Test F1: {f1:.4f}")
        
    
    print("\n\n--- 📊 Tüm Modellerin Özeti (Test Performansı) ---")
    for label, res in results.items():
        print(f"🏷️ {label}: Acc: {res['accuracy_score']:.4f}, F1: {res['best_f1_score']:.4f}")
        
    print("\n🎉 Tüm Çoklu Etiket Sınıflandırma Modelleri Eğitildi ve Kaydedildi.")


if __name__ == "__main__":
    if not ML_LIBRARIES_AVAILABLE:
        print("\nModel eğitimi başlatılamıyor. Lütfen gerekli kütüphaneleri kurun.")
    else:
        df_train = prepare_data_for_autogluon()
        
        if df_train is not None and len(df_train) > 0:
            target_labels = settings.EMOTION_CATEGORIES
            train_autogluon_model(df_train, target_labels)