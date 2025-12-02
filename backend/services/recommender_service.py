import os
import sys
import joblib
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# AutoGluon import'ları
try:
    from autogluon.tabular import TabularPredictor
    ML_LIBRARIES_AVAILABLE = True
except ImportError:
    ML_LIBRARIES_AVAILABLE = False
    print("⚠️ UYARI: AutoGluon kütüphanesi kurulu değil. Tahmin servisi devre dışı.")


# Projenin kök dizininden model klasörüne ulaşmak için yol ayarı
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ml', 'model'))
BINARIZER_PATH = os.path.join(MODEL_DIR, "multi_label_binarizer.pkl")

print(f"📁 MODEL_DIR: {MODEL_DIR}")
print(f"📄 BINARIZER_PATH: {BINARIZER_PATH}")


class RecommenderService:
    """
    Eğitilmiş AutoGluon Çoklu Etiket Sınıflandırma modellerini yöneten 
    ve tahmin yapan servis katmanı.
    """
    
    # Singleton pattern için class değişkenleri
    _instance: Optional['RecommenderService'] = None
    _is_loaded: bool = False
    
    def __new__(cls):
        """Singleton örneği oluşturur."""
        if cls._instance is None:
            cls._instance = super(RecommenderService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Modelleri ve binarizer'ı belleğe yükler."""
        if not self._is_loaded and ML_LIBRARIES_AVAILABLE:
            print("🚀 RecommenderService başlatılıyor: Modeller belleğe yükleniyor...")
            self.predictors: Dict[str, TabularPredictor] = {}
            self.mlb = None
            
            try:
                # 1. MultiLabelBinarizer'ı Yükle
                self.mlb = joblib.load(BINARIZER_PATH)
                self.target_labels = list(self.mlb.classes_)
                print(f"✅ MultiLabelBinarizer yüklendi. Etiketler: {self.target_labels}")
                
                # 2. Tüm modelleri yükle
                loaded_count = 0
                for emotion in self.target_labels:
                    predictor_path = os.path.join(MODEL_DIR, f'predictor_{emotion}')
                    if os.path.exists(predictor_path):
                        self.predictors[emotion] = TabularPredictor.load(predictor_path)
                        print(f"   ✅ {emotion} yüklendi")
                        loaded_count += 1
                    else:
                        print(f"   ⚠ {emotion} için dosya bulunamadı: {predictor_path}")
                
                if loaded_count == len(self.target_labels):
                    self._is_loaded = True
                    print(f"🎉 {len(self.target_labels)} adet model başarıyla yüklendi.")
                else:
                    print(f"⚠ Eksik modeller var: {loaded_count}/{len(self.target_labels)}")
                    self._is_loaded = True
                
            except FileNotFoundError as e:
                print(f"❌ HATA: Model dosyaları bulunamadı. Lütfen eğitimden emin olun. Eksik dosya: {e}")
                self._is_loaded = False
            except Exception as e:
                print(f"❌ Kritik Hata: Modeller yüklenemedi: {e}")
                import traceback
                traceback.print_exc()
                self._is_loaded = False

    def is_ready(self) -> bool:
        """Servisin tahmin yapmaya hazır olup olmadığını kontrol eder."""
        return self._is_loaded and ML_LIBRARIES_AVAILABLE

    def predict_emotions_with_proba(self, overview_text: str, auto_threshold: bool = True, 
                                   custom_threshold: float = None) -> Tuple[List[str], Dict[str, float], float]:
        """
        Film özetinden duygu tahmini yapar ve olasılık yüzdelerini döndürür.
        
        Args:
            overview_text: Film özeti
            auto_threshold: True ise otomatik threshold belirler, False ise custom_threshold kullanır
            custom_threshold: Manuel threshold değeri (0-1 arası)
        
        Returns:
            Tuple: (duygu_listesi, {duygu: olasılık}, kullanılan_threshold)
        """
        if not self.is_ready():
            print("⚠ Model hazır değil")
            return [], {}, 0.0
        
        try:
            # DataFrame oluştur
            data_dict = {'overview': overview_text}
            for label in self.target_labels:
                data_dict[label] = 0
            
            input_df = pd.DataFrame([data_dict])
            
            print(f"\n🎯 Duygu tahmini yapılıyor: {overview_text[:50]}...")
            
            # Her duygu için olasılık tahmini
            emotion_probs = {}
            
            for label in self.predictors:
                try:
                    # Olasılık tahmini yap
                    proba_df = self.predictors[label].predict_proba(input_df)
                    
                    # P(1) olasılığını al (duygunun var olma olasılığı)
                    if not proba_df.empty and len(proba_df.columns) >= 2:
                        prob_positive = float(proba_df.iloc[0, 1])
                        emotion_probs[label] = prob_positive
                    else:
                        emotion_probs[label] = 0.0
                        
                except Exception as e:
                    print(f"   ❌ {label} olasılık hatası: {e}")
                    emotion_probs[label] = 0.0
            
            # AKILLI THRESHOLD BELİRLEME
            if auto_threshold:
                # Strateji 1: Ortalamanın üstündeki değerleri al
                all_probs = list(emotion_probs.values())
                if all_probs:
                    avg_prob = sum(all_probs) / len(all_probs)
                    max_prob = max(all_probs)
                    
                    # Dinamik threshold hesapla
                    if max_prob > 0.7:
                        # Güçlü tahmin varsa threshold yüksek tut
                        threshold = 0.5
                    elif max_prob > 0.4:
                        # Orta güçte tahminler
                        threshold = max(0.3, avg_prob * 0.8)
                    else:
                        # Zayıf tahminler - daha düşük threshold
                        threshold = 0.2
                    
                    # Minimum 0.2, maksimum 0.6
                    threshold = max(0.2, min(0.6, threshold))
                else:
                    threshold = 0.3
            else:
                threshold = custom_threshold if custom_threshold is not None else 0.3
            
            print(f"🎯 Otomatik threshold: {threshold:.2f}")
            
            # Threshold üzerindeki duyguları belirle
            predicted_emotions = []
            for label, prob in emotion_probs.items():
                if prob >= threshold:
                    predicted_emotions.append(label)
            
            # Olasılıkları büyükten küçüğe sırala
            sorted_emotions = sorted(emotion_probs.items(), key=lambda x: x[1], reverse=True)
            
            print(f"\n📈 Duygu Olasılıkları:")
            for emotion, prob in sorted_emotions:
                if prob > 0:
                    star = "⭐⭐⭐" if prob >= 0.7 else "⭐⭐" if prob >= 0.4 else "⭐"
                    print(f"   {emotion:10} {prob:>5.1%} {star}")
            
            print(f"\n✅ Seçilen Duygular: {predicted_emotions}")
            
            return predicted_emotions, emotion_probs, threshold
            
        except Exception as e:
            print(f"❌ Tahmin hatası: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return [], {}, 0.3

    def predict_emotions(self, overview_text: str) -> List[str]:
        """
        Film özetinden duygu tahmini yapar (basit versiyon).
        Otomatik threshold kullanır.
        """
        emotions, _, _ = self.predict_emotions_with_proba(overview_text, auto_threshold=True)
        return emotions


# FastAPI'de bağımlılık olarak kolayca kullanmak için bir fonksiyon
def get_recommender_service() -> RecommenderService:
    """Singleton RecommenderService örneğini döndürür."""
    return RecommenderService()