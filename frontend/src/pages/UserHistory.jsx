import React, { useEffect, useState } from "react";
import axios from "axios";

const UserActivityPage = () => {
  const [history, setHistory] = useState([]);
  const [liked, setLiked] = useState([]);
  const [loading, setLoading] = useState(true);

  const [activeTab, setActiveTab] = useState("history");

  const token = localStorage.getItem("token");

  // -----------------------
  // HISTORY GETIRME
  // -----------------------
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await axios.get("http://localhost:8000/history?limit=100&page=1", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        console.log("History gelen:", res.data);

        const items = res.data.items || [];

        // İzlenenler
        const watchedList = items
          .filter((i) => i.interaction === "watched")
          .map((i) => i);

        // Beğenilenler
        const likedList = items
          .filter((i) => i.interaction === "liked")
          .map((i) => i);

        setHistory(watchedList);
        setLiked(likedList);

      } catch (err) {
        console.log("History fetch error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h1>Kullanıcı Aktivitesi</h1>

      {/* TAB MENU */}
      <div style={{ display: "flex", gap: "20px", marginBottom: "20px" }}>
        <button
          onClick={() => setActiveTab("history")}
          style={{
            padding: "10px",
            background: activeTab === "history" ? "#333" : "#eee",
            color: activeTab === "history" ? "white" : "black",
            borderRadius: "8px",
            border: "none",
            cursor: "pointer",
          }}
        >
          İzlenen Filmler
        </button>

        <button
          onClick={() => setActiveTab("liked")}
          style={{
            padding: "10px",
            background: activeTab === "liked" ? "#333" : "#eee",
            color: activeTab === "liked" ? "white" : "black",
            borderRadius: "8px",
            border: "none",
            cursor: "pointer",
          }}
        >
          Beğenilen Filmler
        </button>
      </div>

      {/* ---------------------- */}
      {/*     HISTORY TAB        */}
      {/* ---------------------- */}

      {activeTab === "history" && (
        <div>
          <h2>İzlenen Filmler</h2>

          {loading ? (
            <p>Yükleniyor...</p>
          ) : history.length === 0 ? (
            <p>Henüz izlediğiniz bir film yok.</p>
          ) : (
            <ul>
              {history.map((item) => (
                <li key={item.id}>
                  <strong>Movie ID:</strong> {item.movie_id} <br />
                  <strong>Tarih:</strong> {new Date(item.created_at).toLocaleString()}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* ---------------------- */}
      {/*        LIKED TAB       */}
      {/* ---------------------- */}

      {activeTab === "liked" && (
        <div>
          <h2>Beğenilen Filmler</h2>

          {loading ? (
            <p>Yükleniyor...</p>
          ) : liked.length === 0 ? (
            <p>Henüz beğendiğiniz film yok.</p>
          ) : (
            <ul>
              {liked.map((item) => (
                <li key={item.id}>
                  <strong>Movie ID:</strong> {item.movie_id} <br />
                  <strong>Tarih:</strong> {new Date(item.created_at).toLocaleString()}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default UserActivityPage;
