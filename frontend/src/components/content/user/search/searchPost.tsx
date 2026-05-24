import React, { useEffect, useRef, useState } from "react";
import ListPost from "../profile/profilePost";
import "./searchPost.css";

interface Props {
  posts: any[];
}

const SearchPost = ({ posts }: Props) => {
  const [isEnd, setIsEnd] = useState(false);
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const el = endRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setIsEnd(true);
        }
      },
      {
        root: null, // 👈 dùng window (QUAN TRỌNG)
        threshold: 0.8,
      }
    );

    observer.observe(el);

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    setIsEnd(false);
  }, [posts]);

  const handleBackToTop = () => {
    const container = document.querySelector(".main-right-side");
    if (container) {
      container.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    }
  };

  if (!posts || posts.length === 0) {
    return <p className="no-post">Không tìm thấy bài đăng</p>;
  }

  return (
    <div className="tab-content-post">
      {posts.map((post) => (
        <ListPost key={post._id} listPostSearch={[post]} />
      ))}

      <div ref={endRef} style={{ height: 10 }} />

      {isEnd && (
        <div className="search-end">
          <p>Không còn nội dung tìm kiếm</p>

          <span className="back-to-top" onClick={handleBackToTop}>
            Quay lại đầu trang
          </span>
        </div>
      )}
    </div>
  );
};

export default SearchPost;