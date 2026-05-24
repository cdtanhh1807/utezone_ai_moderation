import "./sharePostModal.css";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { postAPI } from "../../../../services/PostService";
import AccountService from "../../../../services/AccountService";
import ChevronLeftOutlinedIcon from "@mui/icons-material/ChevronLeftOutlined";
import ChevronRightOutlinedIcon from "@mui/icons-material/ChevronRightOutlined";
import MoreHorizOutlinedIcon from "@mui/icons-material/MoreHorizOutlined";
import type { Post } from "../../../../types/Post";
import type { UserInfo } from "../../../../types/Account";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import PublicIcon from "@mui/icons-material/Public";
import SecurityIcon from "@mui/icons-material/Security";
import BookmarkIcon from "@mui/icons-material/Bookmark";
import DepartmentMultiSelect from "./departmentSelect";
import { ToastService } from "../../../../services/ToastService";

interface SharePostModalProps {
  isOpen: boolean;
  onClose: () => void;
  postId: string | null;
  onShared?: () => void;
}

const backdrop = { hidden: { opacity: 0 }, visible: { opacity: 1 } };
const modal = {
  hidden: { opacity: 0, scale: 0.8, y: 50 },
  visible: { opacity: 1, scale: 1, y: 0 },
};

const SharePostModal = ({
  isOpen,
  onClose,
  postId,
  onShared,
}: SharePostModalProps) => {
  const [originalPost, setOriginalPost] = useState<Post | null>(null);
  const [currentUser, setCurrentUser] = useState<UserInfo | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [visibility, setVisibility] = useState<"public" | "follow" | "private">(
    "public"
  );
  const menuRef = useRef<HTMLDivElement | null>(null);
  const [selectedDepartments, setSelectedDepartments] = useState<string[]>([]);
  const visibilityText = {
    public: "Công khai",
    follow: "Người theo dõi",
    private: "Chỉ mình tôi",
  };
  const visibilityIcon = {
    public: <PublicIcon />,
    follow: <BookmarkIcon />,
    private: <SecurityIcon />,
  };

  useEffect(() => {
    if (!postId) return;

    postAPI
      .getById(postId)
      .then((data) => {
        setOriginalPost(data.post);
        setCurrentIndex(0);
        return AccountService.get_account_info(data.post.createdBy);
      })
      .then((userData) => setCurrentUser(userData))
      .catch((err) =>
        console.error("❌ Lỗi load bài gốc hoặc thông tin user:", err)
      );
  }, [postId]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleShare = async () => {
    if (!postId) return;

    setLoading(true);
    try {
      await postAPI.sharePost(postId, {
        title: title.trim(),
        content: content.trim(),
        visibility: visibility,
        status: "active",
        category: selectedDepartments,
      });

      ToastService.success("Chia sẻ bài viết thành công!");
      onClose();
      onShared?.();

      window.location.href = "/home";
    } catch (err) {
      console.error("❌ Lỗi share:", err);
      ToastService.error("Đã xảy ra lỗi");
    }
    setLoading(false);
  };

  if (!originalPost || !isOpen) return null;

  const previews = originalPost.thumbnails_url || [];

  return createPortal(
    <AnimatePresence>
      <motion.div
        className="modal-backdrop"
        style={{ zIndex: 9999 }}
        variants={backdrop}
        initial="hidden"
        animate="visible"
        exit="hidden"
        onClick={onClose}
      >
        <motion.div
          className="sp-modal-container"
          variants={modal}
          initial="hidden"
          animate="visible"
          exit="hidden"
          onClick={(e) => e.stopPropagation()}
        >
          <h2 className="modal-title">Chia sẻ bài viết</h2>

          <div className="share-layout">
            {/* LEFT — ORIGINAL POST */}
            <div className="share-left">
              <div className="postInfo">
                <img
                  className="postInfoImg"
                  src={currentUser?.avatar || "https://i.pravatar.cc/150?img=1"}
                />
                <div className="postInfoName">{currentUser?.fullName || "Đang tải..."}</div>
                <div className="timingInfo">
                  • {new Date(originalPost.createdAt).toLocaleString("vi-VN")}
                </div>
                <button className="optionPost">
                  <MoreHorizOutlinedIcon />
                </button>
              </div>

              <div className="share-original-content">{originalPost.content}</div>

              {previews.length > 0 && (
                <div className="share-slider">
                  {previews[currentIndex].endsWith(".mp4") ? (
                    <video controls className="share-media">
                      <source src={previews[currentIndex]} type="video/mp4" />
                    </video>
                  ) : (
                    <img src={previews[currentIndex]} className="share-media" />
                  )}
                  {currentIndex > 0 && (
                    <ChevronLeftOutlinedIcon
                      className="share-nav-left"
                      onClick={() => setCurrentIndex((prev) => prev - 1)}
                    />
                  )}
                  {currentIndex < previews.length - 1 && (
                    <ChevronRightOutlinedIcon
                      className="share-nav-right"
                      onClick={() => setCurrentIndex((prev) => prev + 1)}
                    />
                  )}
                </div>
              )}

              <div className="share-thumbs">
                {previews.map((url, idx) => (
                  <img
                    key={idx}
                    src={url}
                    className={`share-thumb ${idx === currentIndex ? "active" : ""}`}
                    onClick={() => setCurrentIndex(idx)}
                  />
                ))}
              </div>
            </div>

            {/* RIGHT — SHARE INPUTS */}
            <div className="share-right">
              <textarea
                className="share-title"
                placeholder="Tiêu đề cho bài share..."
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
              <textarea
                className="share-content"
                placeholder="Bạn muốn nói gì về bài viết này?"
                value={content}
                onChange={(e) => setContent(e.target.value)}
              />

              <div className="visibilitySelector" ref={menuRef}>
                <span className="dots" onClick={() => setMenuOpen((prev) => !prev)}>
                  {visibilityIcon[visibility]}
                  {visibilityText[visibility]} <KeyboardArrowDownIcon />
                </span>
                {menuOpen && (
                  <div className="visibilityMenu">
                    <div
                      className={`visibilityItem ${visibility === "public" ? "active" : ""}`}
                      onClick={() => setVisibility("public")}
                    >
                      <PublicIcon /> Công khai
                    </div>
                    <div
                      className={`visibilityItem ${visibility === "follow" ? "active" : ""}`}
                      onClick={() => setVisibility("follow")}
                    >
                      <BookmarkIcon /> Người theo dõi
                    </div>
                    <div
                      className={`visibilityItem ${visibility === "private" ? "active" : ""}`}
                      onClick={() => setVisibility("private")}
                    >
                      <SecurityIcon /> Chỉ mình tôi
                    </div>
                  </div>
                )}
              </div>

              <div className="selectDepartment">
                <DepartmentMultiSelect
                  selectedDepartments={selectedDepartments}
                  setSelectedDepartments={setSelectedDepartments}
                />
              </div>

              <button className="share-btn" onClick={handleShare} disabled={loading}>
                {loading ? "Đang chia sẻ..." : "Chia sẻ"}
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>,
    document.body
  );
};

export default SharePostModal;
