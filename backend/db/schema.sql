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
    duration INT,                 -- dakika cinsinden süre
    language VARCHAR(50),
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 2. Emotions (AutoML Target Etiketleri)
-- ==========================================
CREATE TABLE IF NOT EXISTS emotions (
    emotion_id SERIAL PRIMARY KEY,
    movie_id INT REFERENCES movies(movie_id) ON DELETE CASCADE,
    emotion_label VARCHAR(50) NOT NULL,  -- örn: sad, dark, humorous, feel_good
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 3. Users Tablosu (Login Destekli)
-- ==========================================
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,   -- şifre hashlenmiş olarak saklanacak
    mood VARCHAR(50),                      -- örn: happy, sad, neutral
    preferred_genre VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);


-- ==========================================
-- 4. User History (öneri sistemi için)
-- ==========================================
CREATE TABLE IF NOT EXISTS user_history (
    history_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    movie_id INT REFERENCES movies(movie_id) ON DELETE CASCADE,
    interaction VARCHAR(50),        -- viewed, liked, clicked
    watch_date TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 5. Movie Tags (opsiyonel, daha detaylı filtreleme için)
-- ==========================================
CREATE TABLE IF NOT EXISTS movie_tags (
    tag_id SERIAL PRIMARY KEY,
    movie_id INT REFERENCES movies(movie_id) ON DELETE CASCADE,
    tag VARCHAR(50),                -- örn: thriller, romance, action
    created_at TIMESTAMP DEFAULT NOW()
);
