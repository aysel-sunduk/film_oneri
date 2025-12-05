"""
Film verilerine AutoGluon modeli kullanarak ÇOKLU duygu etiketleri atayan script.
Eğitilmiş AutoGluon modelini kullanarak film özetlerinden duygu tahmini yapar.
"""

import sys
import os
from typing import List, Optional

# Proje kök dizinini Python path'ine ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(backend_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.db.connection import get_db_session
from backend.db.models import Movie, Emotion
from backend.config import settings
from backend.services.recommender_service import get_recommender_service


def seed_emotions(clear_existing: bool = False, threshold: float = 0.3, auto_threshold: bool = True):
    """
    Eğitilmiş AutoGluon modelini kullanarak veritabanındaki filmlere duygu etiketleri atar.
    
    Args:
        clear_existing: True ise mevcut duygu kayıtlarını siler
        threshold: Duygu kabul eşiği (0-1 arası). auto_threshold=True ise kullanılmaz.
        auto_threshold: True ise otomatik threshold belirler, False ise threshold parametresini kullanır
    """
    print("🚀 AutoGluon Model Servisi Başlatılıyor...")
    
    # AutoGluon model servisini yükle
    recommender = get_recommender_service()
    
    if not recommender.is_ready():
        print("❌ Model servisi hazır değil!")
        print("📝 Lütfen önce modeli eğitin: python backend/ml/automl_train.py")
        return
    
    print(f"✅ Model servisi hazır. {len(recommender.target_labels)} duygu kategorisi yüklendi.")
    print(f"📋 Duygu kategorileri: {', '.join(recommender.target_labels)}")
    
    session = get_db_session()
    
    try:
        print("\n🎬 Duygu Etiketleme Başlatılıyor...")
        
        if clear_existing:
            deleted = session.query(Emotion).delete()
            session.commit()
            print(f"🗑️ {deleted} mevcut duygu kaydı silindi.")
        
        # Overview'u olan filmleri al
        movies = session.query(Movie).filter(
            Movie.overview.isnot(None),
            Movie.overview != "",
            Movie.overview != " "
        ).all()
        
        print(f"📽️ Toplam {len(movies)} film bulundu (overview'u olan).")
        
        # Sadece boş olan filmleri etiketlemek için filtreleme
        if not clear_existing:
             movies_to_process = [
                m for m in movies 
                if not session.query(Emotion).filter(Emotion.movie_id == m.movie_id).first()
            ]
             print(f"🔄 Etiketlenecek {len(movies_to_process)} yeni film var.")
        else:
            movies_to_process = movies
            print(f"🔄 Tüm {len(movies_to_process)} film yeniden etiketlenecek.")
        
        if not movies_to_process:
            print("✅ Etiketlenecek yeni film yok.")
            return
        
        # İstatistik takibi
        created_count = 0
        updated_count = 0
        skipped_count = 0
        emotion_counts = {e: 0 for e in settings.EMOTION_CATEGORIES}

        print(f"\n📊 Threshold: {'Otomatik' if auto_threshold else f'{threshold:.2f}'}")
        print("=" * 60)
        
        for i, movie in enumerate(movies_to_process):
            try:
                # AutoGluon modeli ile duygu tahmini yap
                predicted_emotions, emotion_probs, used_threshold = recommender.predict_emotions_with_proba(
                    movie.overview,
                    auto_threshold=auto_threshold,
                    custom_threshold=threshold if not auto_threshold else None
                )
                
                # Mevcut etiketleri kontrol et
                existing_emotions = session.query(Emotion).filter(
                    Emotion.movie_id == movie.movie_id
                ).all()
                existing_emotion_labels = {e.emotion_label for e in existing_emotions}
                
                # Yeni etiketleri ekle
                added_any = False
                for emotion in predicted_emotions:
                    if emotion not in existing_emotion_labels:
                new_emotion = Emotion(
                    movie_id=movie.movie_id,
                            emotion_label=emotion
                )
                session.add(new_emotion)
                        emotion_counts[emotion] += 1
                created_count += 1
                        added_any = True
                
                if added_any:
                    updated_count += 1
                else:
                    skipped_count += 1
                
                # İlerleme göster
                if (i + 1) % 100 == 0:
                    print(f"  ⏳ İşlendi: {i + 1}/{len(movies_to_process)} | "
                          f"Etiketlenen: {updated_count} | "
                          f"Atlanan: {skipped_count}")
                    session.commit()  # Her 100'de bir commit
                    
            except Exception as e:
                print(f"  ⚠️ Film {movie.movie_id} için hata: {e}")
                skipped_count += 1
                continue
        
        # Son commit
        session.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ İşlem tamamlandı!")
        print(f"   📝 Toplam işlenen film: {len(movies_to_process)}")
        print(f"   ✨ Yeni etiketlenen film: {updated_count}")
        print(f"   🏷️  Toplam oluşturulan etiket: {created_count}")
        print(f"   ⏭️  Atlanan film: {skipped_count}")
        
        print("\n📊 Duygu Dağılımı:")
        for emotion, count in sorted(emotion_counts.items(), key=lambda x: -x[1]):
            if count > 0:
                print(f"   {emotion:12} : {count:4} film")
        
        # Toplam istatistik
        total_emotions = session.query(Emotion).count()
        print(f"\n📈 Veritabanındaki toplam duygu kaydı: {total_emotions}")
            
    except Exception as e:
        session.rollback()
        print(f"\n❌ Hata oluştu: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="AutoGluon modeli kullanarak film verilerine duygu etiketleri ata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnek kullanımlar:
  # Mevcut etiketleri sil ve yeniden etiketle (otomatik threshold)
  python backend/ml/seed_emotions.py --clear
  
  # Sadece yeni filmleri etiketle (otomatik threshold)
  python backend/ml/seed_emotions.py
  
  # Manuel threshold ile etiketle
  python backend/ml/seed_emotions.py --clear --threshold 0.4 --no-auto-threshold
        """
    )
    parser.add_argument(
        '--clear', 
        action='store_true', 
        help='Mevcut duygu kayıtlarını sil ve tüm filmleri yeniden etiketle'
    )
    parser.add_argument(
        '--threshold', 
        type=float, 
        default=0.3, 
        help='Duygu kabul eşiği (0-1 arası, varsayılan: 0.3). --no-auto-threshold ile kullanılır.'
    )
    parser.add_argument(
        '--no-auto-threshold',
        action='store_true',
        help='Otomatik threshold kullanma, --threshold parametresini kullan'
    )
    args = parser.parse_args()
    
    seed_emotions(
        clear_existing=args.clear, 
        threshold=args.threshold,
        auto_threshold=not args.no_auto_threshold
    )