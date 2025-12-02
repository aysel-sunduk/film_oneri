"""Hugging Face'den movies dataset'ini indirir ve veritabanına ekler"""

import sys
import os
import pandas as pd
from datetime import datetime, date
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from datasets import load_dataset
    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False
    print("⚠️  'datasets' kütüphanesi yüklü değil. Yüklemek için: pip install datasets")

from backend.db.connection import get_db_session
from backend.db.models import Movie


def download_dataset() -> pd.DataFrame:
    """Hugging Face'den dataset'i indirir"""
    if not DATASETS_AVAILABLE:
        raise ImportError("'datasets' kütüphanesi gerekli. pip install datasets")
    
    print("📥 Hugging Face'den dataset indiriliyor...")
    dataset = load_dataset("Pablinho/movies-dataset")
    
    # DataFrame'e çevir
    df = dataset['train'].to_pandas()
    
    print(f"✅ {len(df)} film indirildi")
    print(f"📊 Kolonlar: {df.columns.tolist()}")
    
    return df


def parse_release_date(date_str) -> Optional[date]:
    """
    Release date string'ini date objesine dönüştürür.
    Modelde Date tipinde olduğu için date objesi döndürmeliyiz.
    """
    if pd.isna(date_str) or date_str == '' or str(date_str).strip() == '':
        return None
    
    date_str = str(date_str).strip()
    
    # Geçersiz formatları filtrele (çok kısa, sayısal değerler, özel karakterler)
    if len(date_str) < 4:
        return None
    
    # Sadece sayı içeren ve mantıksız değerleri filtrele (örn: "61.328", " - Magic Tricks")
    if not any(c.isdigit() for c in date_str[:4]):
        return None
    
    # YYYY-MM-DD formatını dene
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        pass
    
    # YYYY-MM formatını dene (ayın ilk günü olarak)
    try:
        return datetime.strptime(date_str, '%Y-%m').date()
    except ValueError:
        pass
    
    # Sadece yıl (YYYY) formatını dene
    if date_str.isdigit() and len(date_str) == 4:
        try:
            year = int(date_str)
            if 1900 <= year <= 2100:  # Mantıklı yıl aralığı
                return date(year, 1, 1)  # Yılın ilk günü
        except (ValueError, OverflowError):
            pass
    
    # Geçersiz format
    return None


def clean_and_transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Dataset'i veritabanı formatına dönüştürür (tam eşleşme)"""
    print("\n🔄 Veri temizleniyor ve dönüştürülüyor...")
    
    # Dataset kolonları → Veritabanı kolonları (tam eşleşme)
    df_clean = pd.DataFrame()
    
    # Direkt mapping (kolon isimleri küçük harf, underscore)
    df_clean['title'] = df['Title'].fillna('Unknown')
    
    # Release_Date'i date objesine dönüştür (model Date tipinde)
    df_clean['release_date'] = df['Release_Date'].apply(parse_release_date)
    
    df_clean['overview'] = df['Overview'].fillna('')
    df_clean['popularity'] = pd.to_numeric(df['Popularity'], errors='coerce')
    df_clean['vote_count'] = pd.to_numeric(df['Vote_Count'], errors='coerce')
    df_clean['vote_average'] = pd.to_numeric(df['Vote_Average'], errors='coerce')
    df_clean['original_language'] = df['Original_Language'].fillna('en')
    df_clean['genre'] = df['Genre'].fillna('')
    df_clean['poster_url'] = df['Poster_Url'].fillna('')
    
    # Overview boş olanları filtrele
    df_clean = df_clean[df_clean['overview'].str.strip() != '']
    
    # Title boş olanları filtrele
    df_clean = df_clean[df_clean['title'].str.strip() != '']
    
    # Geçersiz release_date sayısını göster
    invalid_dates = df_clean['release_date'].isna().sum()
    if invalid_dates > 0:
        print(f"⚠️  {invalid_dates} film için geçersiz release_date (None olarak ayarlandı)")
    
    print(f"✅ {len(df_clean)} film temizlendi (overview/title boş olanlar filtrelendi)")
    print(f"📊 Kolonlar: {df_clean.columns.tolist()}")
    
    return df_clean


def import_to_database(df: pd.DataFrame, clear_existing: bool = False):
    """Veritabanına filmleri ekler"""
    session = get_db_session()
    
    try:
        if clear_existing:
            print("\n🗑️  Mevcut filmler siliniyor...")
            deleted = session.query(Movie).delete()
            session.commit()
            print(f"✅ {deleted} film silindi")
        
        print(f"\n💾 {len(df)} film veritabanına ekleniyor...")
        
        added_count = 0
        skipped_count = 0
        
        for idx, row in df.iterrows():
            try:
                # Aynı başlık ve release_date varsa atla (duplicate kontrolü)
                existing = session.query(Movie).filter(
                    Movie.title == row['title'],
                    Movie.release_date == row['release_date']
                ).first()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Movie objesi oluştur (dataset kolonları ile tam eşleşme)
                # release_date zaten date objesi veya None (parse_release_date'den geliyor)
                movie = Movie(
                    title=row['title'],
                    release_date=row['release_date'],  # Zaten date objesi veya None
                    overview=row['overview'],
                    popularity=float(row['popularity']) if pd.notna(row['popularity']) else None,
                    vote_count=int(row['vote_count']) if pd.notna(row['vote_count']) else None,
                    vote_average=float(row['vote_average']) if pd.notna(row['vote_average']) else None,
                    original_language=row['original_language'] if pd.notna(row['original_language']) else 'en',
                    genre=row['genre'] if pd.notna(row['genre']) and str(row['genre']).strip() != '' else None,
                    poster_url=row['poster_url'] if pd.notna(row['poster_url']) and str(row['poster_url']).strip() != '' else None,
                )
                
                session.add(movie)
                added_count += 1
                
                if (added_count + skipped_count) % 500 == 0:
                    print(f"  İşleniyor: {added_count + skipped_count}/{len(df)}")
                    session.commit()  # Her 500'de bir commit
                    
            except Exception as e:
                print(f"⚠️  Hata (satır {idx}): {e}")
                session.rollback()
                skipped_count += 1
                continue
        
        session.commit()
        
        print(f"\n✅ {added_count} yeni film eklendi")
        print(f"⏭️  {skipped_count} film atlandı (duplicate veya hata)")
        
        # İstatistikler
        total_movies = session.query(Movie).count()
        print(f"\n📊 Toplam film sayısı: {total_movies}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Hata: {e}")
        raise
    finally:
        session.close()


def main(clear_existing: bool = False):
    """Ana fonksiyon"""
    print("="*60)
    print("🎬 Movies Dataset Import")
    print("="*60)
    
    # 1. Dataset'i indir
    df = download_dataset()
    
    # 2. Veriyi temizle ve dönüştür
    df_clean = clean_and_transform_data(df)
    
    # 3. Veritabanına ekle
    import_to_database(df_clean, clear_existing=clear_existing)
    
    print("\n" + "="*60)
    print("✅ İşlem tamamlandı!")
    print("="*60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Hugging Face movies dataset'ini indir ve veritabanına ekle")
    parser.add_argument('--clear', action='store_true', help='Mevcut filmleri sil')
    args = parser.parse_args()
    
    main(clear_existing=args.clear)

