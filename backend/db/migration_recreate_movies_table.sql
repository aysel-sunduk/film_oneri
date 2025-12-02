-- =====================================================
-- Movies Tablosunu Yeniden Oluşturma
-- Hugging Face Dataset kolonları ile tam eşleşme
-- =====================================================

-- ⚠️  DİKKAT: Bu script mevcut movies tablosunu siler ve yeniden oluşturur!
-- ⚠️  Tüm film verileri silinecek!
-- ⚠️  Önce yedek al!

-- 1. İlişkili tablolardaki verileri temizle (foreign key hatalarını önlemek için)
DELETE FROM emotions;
DELETE FROM movie_tags;
DELETE FROM user_history;

-- 2. Foreign key constraint'leri geçici olarak kaldır
ALTER TABLE IF EXISTS emotions DROP CONSTRAINT IF EXISTS emotions_movie_id_fkey;
ALTER TABLE IF EXISTS movie_tags DROP CONSTRAINT IF EXISTS movie_tags_movie_id_fkey;
ALTER TABLE IF EXISTS user_history DROP CONSTRAINT IF EXISTS user_history_movie_id_fkey;

-- 3. Eski movies tablosunu sil
DROP TABLE IF EXISTS movies CASCADE;

-- 4. Sequence'i sil (yeniden oluşturulacak)
DROP SEQUENCE IF EXISTS movies_movie_id_seq CASCADE;

-- 5. Yeni movies tablosunu oluştur (Dataset kolonları ile tam eşleşme)
CREATE TABLE movies (
    movie_id SERIAL PRIMARY KEY,
    
    -- Dataset kolonları (tam eşleşme)
    title VARCHAR(255) NOT NULL,                    -- Title
    release_date DATE,                               -- Release_Date
    overview TEXT NOT NULL,                          -- Overview
    popularity DOUBLE PRECISION,                     -- Popularity
    vote_count INTEGER,                              -- Vote_Count
    vote_average DOUBLE PRECISION,                   -- Vote_Average
    original_language VARCHAR(10) DEFAULT 'en',      -- Original_Language
    genre VARCHAR(255),                              -- Genre
    poster_url TEXT,                                 -- Poster_Url
    
    -- Sistem kolonları
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Index'ler ekle (performans için)
CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movies_release_date ON movies(release_date);
CREATE INDEX idx_movies_genre ON movies(genre);
CREATE INDEX idx_movies_popularity ON movies(popularity);
CREATE INDEX idx_movies_vote_average ON movies(vote_average);
CREATE INDEX idx_movies_vote_count ON movies(vote_count);
CREATE INDEX idx_movies_original_language ON movies(original_language);

-- 7. Foreign key constraint'leri yeniden ekle
ALTER TABLE emotions 
ADD CONSTRAINT emotions_movie_id_fkey 
FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE;

ALTER TABLE movie_tags 
ADD CONSTRAINT movie_tags_movie_id_fkey 
FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE;

ALTER TABLE user_history 
ADD CONSTRAINT user_history_movie_id_fkey 
FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE;

-- 8. Tablo yapısını kontrol et
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'movies'
ORDER BY ordinal_position;

-- =====================================================
-- Kolon Eşleşmesi:
-- =====================================================
-- Dataset Kolonu          → Veritabanı Kolonu
-- ------------------------------------------------
-- Title                   → title
-- Release_Date            → release_date
-- Overview                 → overview
-- Popularity               → popularity
-- Vote_Count               → vote_count
-- Vote_Average             → vote_average
-- Original_Language        → original_language
-- Genre                    → genre
-- Poster_Url               → poster_url
-- ------------------------------------------------
-- (movie_id ve created_at otomatik eklenir)

