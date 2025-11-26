// src/data/mockData.js

// Bu veri yapısı, backend'den almayı beklediğimiz formatı temsil eder.
export const mockMovies = [
    {
      id: 1,
      title: "Mor Geceler",
      posterUrl: "https://via.placeholder.com/300x450/6A5ACD/FFFFFF?text=Mor+Geceler",
      backdropUrl: "https://via.placeholder.com/1200x400/6A5ACD/FFFFFF?text=Mor+Geceler+Geniş",
      rating: 8.5,
      genre: ["Drama", "Gizem"],
      releaseYear: 2023,
      director: "Elif Kara",
      summary: "Modern bir şehirde geçen, kayıp bir sanat eserinin peşindeki iki dedektifin hikayesi. Her köşe başında yeni bir sır açığa çıkıyor.",
      cast: ["Oyuncu A", "Oyuncu B", "Oyuncu C"]
    },
    {
      id: 2,
      title: "Yıldız Tozu",
      posterUrl: "https://via.placeholder.com/300x450/483D8B/FFFFFF?text=Yildiz+Tozu",
      backdropUrl: "https://via.placeholder.com/1200x400/483D8B/FFFFFF?text=Yıldız+Tozu+Geniş",
      rating: 7.9,
      genre: ["Bilim Kurgu", "Aksiyon"],
      releaseYear: 2025,
      director: "Can Uzay",
      summary: "Gelecekte, insanlık yeni bir gezegene göç ederken, bir grup genç, terk edilmiş Dünya'nın sırlarını çözmeye çalışır.",
      cast: ["Oyuncu D", "Oyuncu E", "Oyuncu F"]
    },
    {
      id: 3,
      title: "Sonsuz Orkide",
      posterUrl: "https://via.placeholder.com/300x450/9370DB/FFFFFF?text=Sonsuz+Orkide",
      backdropUrl: "https://via.placeholder.com/1200x400/9370DB/FFFFFF?text=Sonsuz+Orkide+Geniş",
      rating: 9.2,
      genre: ["Romantik", "Fantastik"],
      releaseYear: 2024,
      director: "Deniz Rüzgar",
      summary: "Zamanda yolculuk yapabilen bir botanikçinin, kayıp aşkını bulmak için farklı çağlarda açan nadir bir çiçeği arayışı.",
      cast: ["Oyuncu G", "Oyuncu H", "Oyuncu I"]
    },
    // ... daha fazla film ekleyebilirsiniz
];