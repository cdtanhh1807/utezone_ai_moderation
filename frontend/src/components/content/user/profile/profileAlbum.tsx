import { useEffect, useState } from "react";
import "./profileAlbum.css";
import { postAPI } from "../../../../services/PostService";
import EastIcon from "@mui/icons-material/East";
import { jwtDecode } from "jwt-decode";
import PostDetail from "../post/postDetail";

interface AlbumImage {
  postId: string;
  url: string;
}

function ProfileAlbum() {
  const [images, setImages] = useState<AlbumImage[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalImage, setModalImage] = useState<AlbumImage | null>(null);
  const [activePost, setActivePost] = useState<any>(null);
  const [isPostDetailOpen, setIsPostDetailOpen] = useState(false);

  const token = localStorage.getItem("token");
  let currentUserEmail: string | null = null;

  if (!currentUserEmail && token) {
    try {
      interface JwtPayload {
        sub: string;
        exp: number;
        per: string;
        role: string;
      }
      const decoded: JwtPayload = jwtDecode<JwtPayload>(token);
      currentUserEmail = decoded.sub;
    } catch (err) {
      console.error("❌ Token không hợp lệ:", err);
    }
  }

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        const res = await postAPI.getByEmail(currentUserEmail!);
        const posts = res.post_list || [];

        const imgs: AlbumImage[] = [];
        posts.forEach((post: any) => {
          if (
            Array.isArray(post.thumbnails_url) &&
            post.thumbnails_url.length > 0
          ) {
            post.thumbnails_url.forEach((url: string) => {
              imgs.push({
                postId: post._id,
                url,
              });
            });
          }
        });

        console.log("Images for album:", imgs);
        setImages(imgs);
      } catch (err) {
        console.error("Lỗi khi load album:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  if (loading) return <p>Đang tải album...</p>;

  const openModal = (img: AlbumImage) => setModalImage(img);
  const closeModal = () => setModalImage(null);

  const handleOpenPost = async (postId: string) => {
    try {
      const res = await postAPI.getById(postId);
      const post = res.post || res;

      setActivePost(post);
      setIsPostDetailOpen(true);
    } catch (err) {
      console.error("Lỗi mở bài viết", err);
    }
  };
  const refreshPost = async (postId: string) => {
    const updated = await postAPI.getById(postId);
    const updatedPost = updated.post || updated;
    setActivePost(updatedPost);
  };

  const openOriginalPost = async (originalPostId: string) => {
    try {
      const res = await postAPI.getById(originalPostId);
      const originalPost = res.post || res;

      setIsPostDetailOpen(false);
      requestAnimationFrame(() => {
        setActivePost(originalPost);
        setIsPostDetailOpen(true);
      });
    } catch (err) {
      console.error("Không lấy được bài viết gốc", err);
    }
  };

  return (
    <div className="album-container">
      <h3 className="album-title">Album ảnh & video</h3>

      {images.length === 0 ? (
        <p>Chưa có ảnh nào</p>
      ) : (
        <div className="album-grid">
          {images.map((img, index) => {
            const ext = img.url.split(".").pop()?.toLowerCase();
            const isVideo = ext === "mp4" || ext === "mov" || ext === "webm";

            return (
              <div
                key={index}
                className="album-item"
                onClick={() => openModal(img)}
              >
                {isVideo ? (
                  <video
                    controls
                    preload="metadata"
                    style={{
                      width: "100%",
                      height: "100%",
                      objectFit: "cover",
                    }}
                  >
                    <source src={img.url} type={`video/${ext}`} />
                  </video>
                ) : (
                  <img
                    src={img.url}
                    alt={`media-${index}`}
                    style={{
                      width: "100%",
                      height: "100%",
                      objectFit: "cover",
                    }}
                  />
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Modal */}
      {modalImage && (
        <div className="modal-overlay-album" onClick={closeModal}>
          <div
            className="modal-content-album"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className="modal-link-btn"
              onClick={() => handleOpenPost(modalImage.postId)}
            >
              <EastIcon />
            </button>

            {modalImage.url.endsWith(".mp4") ||
            modalImage.url.endsWith(".mov") ||
            modalImage.url.endsWith(".webm") ? (
              <video controls autoPlay className="modal-media">
                <source
                  src={modalImage.url}
                  type={`video/${modalImage.url.split(".").pop()}`}
                />
                Trình duyệt của bạn không hỗ trợ video.
              </video>
            ) : (
              <img src={modalImage.url} alt="modal" className="modal-media" />
            )}
          </div>
        </div>
      )}

      {isPostDetailOpen && activePost && (
        <PostDetail
          activePost={activePost}
          onClose={() => setIsPostDetailOpen(false)}
          onCommentAdded={refreshPost}
          onOpenOriginalPost={openOriginalPost}
        />
      )}
    </div>
  );
}

export default ProfileAlbum;
