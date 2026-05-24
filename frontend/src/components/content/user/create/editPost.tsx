import "./editPost.css";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect, useRef, useMemo } from "react";
import { createPortal } from "react-dom";
import { postAPI } from "../../../../services/PostService";
import FileService, {
  type UploadResponse,
} from "../../../../services/FileService";
import type { Post } from "../../../../types/Post";
import ChevronLeftOutlinedIcon from "@mui/icons-material/ChevronLeftOutlined";
import ChevronRightOutlinedIcon from "@mui/icons-material/ChevronRightOutlined";
import PublicIcon from "@mui/icons-material/Public";
import SecurityIcon from "@mui/icons-material/Security";
import BookmarkIcon from "@mui/icons-material/Bookmark";
import DepartmentMultiSelect from "./departmentSelect";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import { ToastService } from "../../../../services/ToastService";

interface EditPostProps {
  isOpen: boolean;
  onClose: () => void;
  post: Post | null;
  onPostUpdated?: () => void;
}

interface OldPreview {
  id: string;
  url: string;
}

const backdrop = { hidden: { opacity: 0 }, visible: { opacity: 1 } };
const modal = {
  hidden: { opacity: 0, scale: 0.8, y: 50 },
  visible: { opacity: 1, scale: 1, y: 0 },
};

/* ================== FIX CỐT LÕI ================== */
/* Chuẩn hóa visibility từ DB -> FE */
const normalizeVisibility = (
  value?: string,
): "public" | "follow" | "private" => {
  if (!value) return "public";

  const v = value.toLowerCase();

  if (v === "public") return "public";
  if (v === "follow" || v === "followers") return "follow";
  if (v === "private" || v === "only_me") return "private";

  return "public";
};
/* ================================================= */

const EditPost = ({ isOpen, onClose, post, onPostUpdated }: EditPostProps) => {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [oldPreviews, setOldPreviews] = useState<OldPreview[]>([]);
  const [newFiles, setNewFiles] = useState<File[]>([]);
  const [newPreviews, setNewPreviews] = useState<string[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [visibility, setVisibility] = useState<"public" | "follow" | "private">(
    "public",
  );
  const [selectedDepartments, setSelectedDepartments] = useState<string[]>([]);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  interface OldAttachment {
    id: string;
    name: string;
  }

  const [oldAttachments, setOldAttachments] = useState<OldAttachment[]>([]);
  const [newAttachments, setNewAttachments] = useState<File[]>([]);

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

  /* ================== FIX QUAN TRỌNG ================== */
  const isMediaFile = (fileId: string) => {
    return /\.(jpg|jpeg|png|gif|webp|mp4|mov|avi)$/i.test(fileId);
  };

  const getFileNameFromId = (fileId: string) => {
    const index = fileId.indexOf("_");
    return index !== -1 ? fileId.substring(index + 1) : fileId;
  };

  useEffect(() => {
    if (!post) return;

    setTitle(post.title || "");
    setContent(post.content || "");

    const oldMedia: OldPreview[] = [];
    const oldFiles: OldAttachment[] = [];

    (post.thumbnails || []).forEach((fileId, idx) => {
      const url = post.thumbnails_url?.[idx] || "";

      if (isMediaFile(fileId)) {
        oldMedia.push({ id: fileId, url });
      } else {
        oldFiles.push({
          id: fileId,
          name: getFileNameFromId(fileId),
        });
      }
    });

    setOldPreviews(oldMedia);
    setOldAttachments(oldFiles);

    setNewFiles([]);
    setNewPreviews([]);
    setNewAttachments([]);

    setCurrentIndex(0);
    setVisibility(normalizeVisibility(post.visibility));
    setSelectedDepartments(post.category || []);
  }, [post]);
  /* =================================================== */

  const allPreviews = useMemo(
    () => [...oldPreviews.map((p) => p.url), ...newPreviews],
    [oldPreviews, newPreviews],
  );

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const filesSelected = Array.from(e.target.files || []);
    if (!filesSelected.length) return;

    const mediaFiles: File[] = [];
    const normalFiles: File[] = [];

    filesSelected.forEach((file) => {
      if (file.type.startsWith("image") || file.type.startsWith("video")) {
        mediaFiles.push(file);
      } else {
        normalFiles.push(file);
      }
    });

    // ảnh/video
    if (mediaFiles.length) {
      const previews = mediaFiles.map((f) => URL.createObjectURL(f));

      setNewFiles((prev) => [...prev, ...mediaFiles]);
      setNewPreviews((prev) => {
        const updated = [...prev, ...previews];
        setCurrentIndex(oldPreviews.length + updated.length - 1);
        return updated;
      });
    }

    // file thường
    if (normalFiles.length) {
      setNewAttachments((prev) => [...prev, ...normalFiles]);
    }
  };

  const removeOldAttachment = (index: number) => {
    setOldAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  const removeNewAttachment = (index: number) => {
    setNewAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  const handleDelete = (idx: number) => {
    if (idx < oldPreviews.length) {
      setOldPreviews((prev) => {
        const updated = prev.filter((_, i) => i !== idx);
        setCurrentIndex((i) => Math.max(0, i - 1));
        return updated;
      });
    } else {
      const newIdx = idx - oldPreviews.length;
      setNewFiles((prev) => prev.filter((_, i) => i !== newIdx));
      setNewPreviews((prev) => prev.filter((_, i) => i !== newIdx));
      setCurrentIndex((i) => Math.max(0, i - 1));
    }
  };

  const handleUpdatePost = async () => {
    if (!post) return;

    if (!content.trim()) {
      ToastService.warning("Nội dung không được để trống");
      return;
    }

    setLoading(true);
    try {
      // ====== 1. FILE CŨ ======
      const remainingMediaIds = oldPreviews.map((p) => p.id).filter(Boolean);

      const remainingFileIds = oldAttachments.map((f) => f.id).filter(Boolean);

      // ====== 2. UPLOAD FILE MỚI ======
      let newMediaIds: string[] = [];
      let newFileIds: string[] = [];

      // 👉 upload ảnh/video
      if (newFiles.length) {
        const uploadResults: UploadResponse[] = await Promise.all(
          newFiles.map((f) => FileService.uploadPicture(f)),
        );
        newMediaIds = uploadResults.map((r) => r.file_id);
      }

      // 👉 upload file thường (pdf, docx...)
      if (newAttachments.length) {
        const uploadResults: UploadResponse[] = await Promise.all(
          newAttachments.map((f) => FileService.uploadPicture(f)),
        );
        newFileIds = uploadResults.map((r) => r.file_id);
      }

      // ====== 3. GỘP TẤT CẢ ======
      const finalThumbnails = [
        ...remainingMediaIds,
        ...remainingFileIds,
        ...newMediaIds,
        ...newFileIds,
      ];

      // ====== 4. CALL API ======
      await postAPI.updatePost(post._id, {
        title,
        content,
        thumbnails: finalThumbnails,
        visibility,
        category: selectedDepartments,
      });

      ToastService.success("Cập nhật bài viết thành công!");
      onClose();
      onPostUpdated?.();
    } catch (err) {
      console.error(err);
      ToastService.error("Đã xảy ra lỗi khi cập nhật bài viết.");
    }

    setLoading(false);
  };

  if (!isOpen || !post) return null;

  return createPortal(
    <AnimatePresence>
      <motion.div
        className="modal-backdrop"
        variants={backdrop}
        initial="hidden"
        animate="visible"
        exit="hidden"
        onClick={onClose}
      >
        <motion.div
          className="ep-modal-container"
          variants={modal}
          initial="hidden"
          animate="visible"
          exit="hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* LEFT */}
          <div className="edit-left">
            <div className="ed-carousel-container">
              {allPreviews[currentIndex]?.endsWith(".mp4") ? (
                <video controls className="preview-video">
                  <source src={allPreviews[currentIndex]} />
                </video>
              ) : (
                <img
                  src={allPreviews[currentIndex]}
                  className="preview-image"
                />
              )}
              {currentIndex > 0 && (
                <ChevronLeftOutlinedIcon
                  className="nav-left"
                  onClick={() => setCurrentIndex((i) => i - 1)}
                />
              )}
              {currentIndex < allPreviews.length - 1 && (
                <ChevronRightOutlinedIcon
                  className="nav-right"
                  onClick={() => setCurrentIndex((i) => i + 1)}
                />
              )}
            </div>

            <div className="thumbnail-bar">
              {allPreviews.map((url, idx) => (
                <div key={idx} style={{ position: "relative" }}>
                  <img
                    src={url}
                    className={`thumbnail ${
                      idx === currentIndex ? "active-thumb" : ""
                    }`}
                    onClick={() => setCurrentIndex(idx)}
                  />
                  <span
                    className="delete-thumb"
                    onClick={() => handleDelete(idx)}
                  >
                    ✕
                  </span>
                </div>
              ))}
              <label className="thumbnail add-thumb">
                +
                <input type="file" multiple onChange={handleUpload} />
              </label>
            </div>
          </div>

          {/* RIGHT */}
          <div className="edit-right">
            <textarea
              className="ep-modal-textarea-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Tiêu đề"
            />
            <textarea
              className="ep-modal-textarea-content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Nội dung"
            />

            <div className="attachmentSection">
              <label className="attachBtn">
                📎 Đính kèm tệp
                <input type="file" multiple onChange={handleUpload} />
              </label>

              {(oldAttachments.length > 0 || newAttachments.length > 0) && (
                <div className="attachmentList">
                  {oldAttachments.map((file, idx) => (
                    <div key={`old-${idx}`} className="attachmentItem">
                      <span className="fileName">📄 {file.name}</span>
                      <button
                        className="removeAttachment"
                        onClick={() => removeOldAttachment(idx)}
                      >
                        ✕
                      </button>
                    </div>
                  ))}

                  {newAttachments.map((file, idx) => (
                    <div key={`new-${idx}`} className="attachmentItem">
                      <span className="fileName">📄 {file.name}</span>
                      <button
                        className="removeAttachment"
                        onClick={() => removeNewAttachment(idx)}
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="visibilitySelector">
              <span className="dots" onClick={() => setMenuOpen((p) => !p)}>
                {visibilityIcon[visibility]} {visibilityText[visibility]}
                <KeyboardArrowDownIcon />
              </span>

              {menuOpen && (
                <div className="visibilityMenu">
                  {(["public", "follow", "private"] as const).map((v) => (
                    <div
                      key={v}
                      className={`visibilityItem ${
                        visibility === v ? "active" : ""
                      }`}
                      onClick={() => {
                        setVisibility(v);
                        setMenuOpen(false);
                      }}
                    >
                      {visibilityIcon[v]} {visibilityText[v]}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <DepartmentMultiSelect
              selectedDepartments={selectedDepartments}
              setSelectedDepartments={setSelectedDepartments}
            />

            <button
              className="edit-btn"
              onClick={handleUpdatePost}
              disabled={loading}
            >
              {loading ? "Đang cập nhật..." : "Cập nhật"}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>,
    document.body,
  );
};

export default EditPost;
