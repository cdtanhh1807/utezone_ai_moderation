import { useEffect, useState } from "react";
import FavoriteBorderOutlinedIcon from "@mui/icons-material/FavoriteBorderOutlined";
import CommentService from "../../../../services/CommentService";
import type {
  CommentReply,
  CommentReact,
} from "../../../../types/CommentReply";
import { jwtDecode } from "jwt-decode";

interface ReplyCommentProps {
  postId: string;
  parentId: string;
  userInfoMap: Record<string, { fullName: string; avatar?: string }>;
  newReply?: CommentReply; // ✅ thêm prop này
  onReply: (reply: CommentReply) => void;
}

export interface GetCommentReplyRequest {
  postId: string;
  parentId: string;
}

export default function ReplyComment({
  postId,
  parentId,
  userInfoMap,
  newReply,
  onReply,
}: ReplyCommentProps) {
  const [replies, setReplies] = useState<CommentReply[]>([]);
  const [loading, setLoading] = useState(true);
  const [openMenu, setOpenMenu] = useState<Record<string, boolean>>({});
  const [popoverMap, setPopoverMap] = useState<Record<string, boolean>>({});
  const [userReactMap, setUserReactMap] = useState<Record<string, string>>({});
  const [refreshKey, setRefreshKey] = useState(0);

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

  const fetchReplies = async () => {
    try {
      setLoading(true);
      const data: GetCommentReplyRequest = { postId, parentId };
      const res = await CommentService.getCommentReply(data);

      const list = Array.isArray(res.commentReplys) ? res.commentReplys : [];
      list.sort((a: CommentReply, b: CommentReply) =>
        a.path.localeCompare(b.path),
      );

      setReplies(list);

      // Khởi tạo userReactMap từ react hiện có
      if (currentUserEmail) {
        const map: Record<string, string> = {};
        list.forEach((r: CommentReply) => {
          for (const [type, users] of Object.entries(r.react || {})) {
            if ((users as string[]).includes(currentUserEmail!)) {
              map[r.commentId] = type;
            }
          }
        });
        setUserReactMap(map);
      }
    } catch (err) {
      console.error("Lỗi khi lấy reply:", err);
      setReplies([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReplies();
  }, [postId, parentId, refreshKey]);

  useEffect(() => {
    if (!newReply) return;

    // 👉 force sync lại từ server (QUAN TRỌNG)
    const exists = replies.some((r) => r.commentId === newReply.commentId);

    if (!exists) {
      setReplies((prev) => [...prev, newReply]);
    } else {
      // fallback: reload để chắc chắn không lệch data
      setRefreshKey((prev) => prev + 1);
    }
  }, [newReply]);

  // 🔹 Convert updatedReact từ API thành CommentReact
  const normalizeReact = (react: Record<string, string[]>): CommentReact => ({
    love: react.love || [],
    like: react.like || [],
    haha: react.haha || [],
    wow: react.wow || [],
    sad: react.sad || [],
    angry: react.angry || [],
  });

  // 🔹 Xử lý react cho reply comment
  const handleReplyReact = async (
    commentId: string,
    type: "love" | "like" | "haha" | "wow" | "sad" | "angry",
  ) => {
    try {
      if (!currentUserEmail) return;

      const res = await CommentService.updateCommentReplyReact(
        postId,
        commentId,
        type,
      );

      const updatedReact = normalizeReact(res.react);

      // Cập nhật vào state replies
      setReplies((prev) =>
        prev.map((r) =>
          r.commentId === commentId ? { ...r, react: updatedReact } : r,
        ),
      );

      // Cập nhật userReactMap
      const entry = Object.entries(updatedReact).find(([t, users]) =>
        users.includes(currentUserEmail!),
      );
      setUserReactMap((prev) => ({
        ...prev,
        [commentId]: entry ? entry[0] : "",
      }));
    } catch (err) {
      console.error("❌ Lỗi khi gửi reaction cho reply:", err);
    }
  };
  const handleDeleteReply = async (reply: CommentReply) => {
    try {
      await CommentService.updateStatusCommentReply({
        postId: postId,
        commentId: reply.commentId,
        path: reply.path,
        status: "hidden",
      });

      // 🔥 XÓA KHỎI UI NGAY LẬP TỨC (giống comment chính)
      setReplies((prev) => prev.filter((r) => r.commentId !== reply.commentId));
    } catch (err) {
      console.error("❌ Lỗi khi ẩn reply:", err);
    }
  };
  useEffect(() => {
    const handleClickOutside = () => setOpenMenu({});
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, []);
  const btnStyle: React.CSSProperties = {
    padding: "6px 12px",
    background: "none",
    border: "none",
    cursor: "pointer",
    width: "100%",
    textAlign: "left",
  };

  const btnStyleDanger: React.CSSProperties = {
    ...btnStyle,
    color: "#e53935",
  };
  const renderContentWithTags = (text: string) => {
    const regex = /(@[^#]+#)/g;
    const parts = text.split(regex);

    return parts.map((part, index) => {
      if (part.startsWith("@") && part.endsWith("#")) {
        const cleanTag = part.slice(0, -1); // bỏ dấu #
        return (
          <span key={index} className="tag-user">
            {cleanTag}
          </span>
        );
      }
      return (
        <span key={index} style={{ color: "#000" }}>
          {part}
        </span>
      );
    });
  };

  const formatTimeVN = (time: string) => new Date(time).toLocaleString("vi-VN");
  const isVideo = (url: string) => {
    return (
      url.includes(".mp4") ||
      url.includes(".webm") ||
      url.includes(".mov") ||
      url.includes("video")
    );
  };

  if (loading) return <div>Đang tải reply...</div>;

  return (
    <div className="reply-list">
      {replies.map((reply: CommentReply) => {
        const level = reply.path?.split(";").length || 1;
        return (
          <div
            key={reply.commentId}
            className="comment-card"
            style={{ marginLeft: (level - 1) * 16 + (level - 1) * 16 }}
          >
            {/* AVATAR */}
            <img
              src={userInfoMap[reply.commentBy]?.avatar}
              alt="avatar"
              className="comment-avatar"
            />

            <div className="comment-body">
              {/* HEADER */}
              <div
                className="comment-header"
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <span className="comment-username">
                    {userInfoMap[reply.commentBy]?.fullName || reply.commentBy}
                  </span>
                  <span className="comment-time">
                    {formatTimeVN(reply.createdAt)}
                  </span>
                </div>

                {/* MENU */}
                <div
                  className="comment-options"
                  style={{ position: "relative" }}
                >
                  <button
                    type="button"
                    className="options-btn"
                    onClick={() =>
                      setOpenMenu((prev) => ({
                        ...prev,
                        [reply.commentId]: !prev[reply.commentId],
                      }))
                    }
                  >
                    ⋮
                  </button>

                  {openMenu[reply.commentId] && (
                    <div
                      className="comment-menu"
                      style={{
                        position: "absolute",
                        top: "24px",
                        right: 0,
                        background: "#fff",
                        border: "1px solid #ccc",
                        borderRadius: "6px",
                        zIndex: 1000,
                        boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
                        minWidth: "170px",
                      }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      {/* 👉 CHỦ COMMENT */}
                      {reply.commentBy === currentUserEmail ? (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteReply(reply);
                            setOpenMenu({});
                          }}
                          style={btnStyleDanger}
                        >
                          ❌ Xóa bình luận
                        </button>
                      ) : (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            // TODO: mở modal report nếu cần
                            setOpenMenu({});
                          }}
                          style={btnStyle}
                        >
                          🚩 Báo cáo bình luận
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* CONTENT */}
              <div className="comment-content">
                {renderContentWithTags(reply.content)}
              </div>
              {reply.thumbnails && reply.thumbnails.length > 0 && (
                <div className="comment-thumbnail">
                  {reply.thumbnails[0] && isVideo(reply.thumbnails[0]) ? (
                    <video
                      src={reply.thumbnails[0]}
                      className="comment-thumbnail-img"
                      controls
                    />
                  ) : (
                    <img
                      src={reply.thumbnails[0]}
                      alt="comment-thumbnail"
                      className="comment-thumbnail-img"
                    />
                  )}
                </div>
              )}

              {/* REACT */}
              <div className="comment-reacts">
                <div
                  className="like-container"
                  onMouseEnter={() =>
                    setPopoverMap((prev) => ({
                      ...prev,
                      [reply.commentId]: true,
                    }))
                  }
                  onMouseLeave={() =>
                    setPopoverMap((prev) => ({
                      ...prev,
                      [reply.commentId]: false,
                    }))
                  }
                >
                  <button
                    type="button"
                    className={`react-btn ${
                      userReactMap[reply.commentId]
                        ? `active-${userReactMap[reply.commentId]}`
                        : ""
                    }`}
                    onClick={() => handleReplyReact(reply.commentId, "love")}
                  >
                    {userReactMap[reply.commentId] === "love" ? (
                      "❤️"
                    ) : userReactMap[reply.commentId] === "like" ? (
                      "👍"
                    ) : userReactMap[reply.commentId] === "haha" ? (
                      "😂"
                    ) : userReactMap[reply.commentId] === "wow" ? (
                      "😮"
                    ) : userReactMap[reply.commentId] === "sad" ? (
                      "😢"
                    ) : userReactMap[reply.commentId] === "angry" ? (
                      "😡"
                    ) : (
                      <FavoriteBorderOutlinedIcon />
                    )}
                  </button>

                  {popoverMap[reply.commentId] && (
                    <div className="emote-popover">
                      {["love", "like", "haha", "wow", "sad", "angry"].map(
                        (e) => {
                          const emojiMap: Record<string, string> = {
                            love: "❤️",
                            like: "👍",
                            haha: "😂",
                            wow: "😮",
                            sad: "😢",
                            angry: "😡",
                          };
                          return (
                            <span
                              key={e}
                              onClick={() =>
                                handleReplyReact(
                                  reply.commentId,
                                  e as
                                    | "love"
                                    | "like"
                                    | "haha"
                                    | "wow"
                                    | "sad"
                                    | "angry",
                                )
                              }
                            >
                              {emojiMap[e]}
                            </span>
                          );
                        },
                      )}
                    </div>
                  )}
                </div>

                {/* COUNT */}
                {Object.values(reply.react || {}).reduce(
                  (s, arr) => s + arr.length,
                  0,
                ) > 0 && (
                  <label className="countReact-Comment">
                    {Object.values(reply.react || {}).reduce(
                      (s, arr) => s + arr.length,
                      0,
                    )}{" "}
                    lượt bày tỏ cảm xúc
                  </label>
                )}

                {/* REPLY BUTTON */}

                <button
                  type="button"
                  className="reply-btn"
                  onClick={() => onReply(reply)}
                >
                  Trả lời
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
