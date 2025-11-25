-- ==========================================
-- 1. Movies Tablosu
-- ==========================================
CREATE TABLE IF NOT EXISTS movies (
    movie_id SERIAL PRIMARY KEY,
    series_title VARCHAR(255) NOT NULL,
    released_year VARCHAR(10),
    genre VARCHAR(255),
    imdb_rating FLOAT,
    meta_score INT,
    overview TEXT NOT NULL,
    director VARCHAR(255),
    star1 VARCHAR(255),
    star2 VARCHAR(255),
    star3 VARCHAR(255),
    star4 VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 2. Emotions (AutoML Target Etiketleri)
-- ==========================================
CREATE TABLE IF NOT EXISTS emotions (
    emotion_id SERIAL PRIMARY KEY,
    movie_id INT REFERENCES movies(movie_id) ON DELETE CASCADE,
    emotion_label VARCHAR(50) NOT NULL,  -- sad, dark, humorous, feel_good
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 3. User History (öneri sistemi için opsiyonel)
-- ==========================================
CREATE TABLE IF NOT EXISTS user_history (
    history_id SERIAL PRIMARY KEY,
    user_id VARCHAR(100),       -- kimlik saklamıyoruz, sadece userId
    movie_id INT REFERENCES movies(movie_id),
    interaction VARCHAR(50),    -- viewed, liked, clicked
    created_at TIMESTAMP DEFAULT NOW()
);
