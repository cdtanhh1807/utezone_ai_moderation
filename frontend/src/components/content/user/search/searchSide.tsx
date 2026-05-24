import { useState, useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { searchAPI } from "../../../../services/SearchService";

import "./searchSide.css";
import SearchPost from "./searchPost";
import SearchUser from "./searchUser";

const SearchSide = () => {
  const location = useLocation();
  const query = new URLSearchParams(location.search);
  const keyword = query.get("keyword") || "";

  const [tab, setTab] = useState<"posts" | "users">("posts");
  const [userResults, setUserResults] = useState<any[]>([]);
  const [postResults, setPostResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // ✅ FIX TYPE (chuẩn)
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!keyword) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        if (tab === "users") {
          const res = await searchAPI.searchAccount(keyword);
          setUserResults(res.account_list || []);
        } else {
          const res = await searchAPI.searchPost(keyword);
          setPostResults(res.post_list || []);
        }
      } catch (err) {
        console.error("❌ Search error:", err);
      } finally {
        setLoading(false);

        // ✅ scroll về đầu (đúng container)
        setTimeout(() => {
          containerRef.current?.scrollTo({
            top: 0,
            behavior: "auto", // ❌ bỏ "instant" (không hợp lệ)
          });
        }, 0);
      }
    };

    fetchData();
  }, [keyword, tab]);

  return (
    <div className="searchSide" ref={containerRef}>
      <h2 className="search-title">
        Kết quả tìm kiếm cho: <span>"{keyword}"</span>
      </h2>

      {/* Tabs */}
      <div className="search-tabs">
        <button
          className={tab === "posts" ? "active" : ""}
          onClick={() => setTab("posts")}
        >
          Bài đăng
        </button>
        <button
          className={tab === "users" ? "active" : ""}
          onClick={() => setTab("users")}
        >
          Mọi người
        </button>
      </div>

      {/* Nội dung */}
      <div className="search-content">
        {loading ? (
          <p>Đang tải...</p>
        ) : tab === "posts" ? (
          <SearchPost
            posts={postResults}
          />
        ) : (
          <SearchUser users={userResults} />
        )}
      </div>
    </div>
  );
};

export default SearchSide;