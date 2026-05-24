import React, { useEffect, useState, useRef } from "react";
import { postAPI } from "../../../../services/PostService";
import { aiAPI } from "../../../../services/AIService";
import AccountService from "../../../../services/AccountService";
import CommentService from "../../../../services/CommentService";
import type { Post } from "../../../../types/Post";
import type { UserInfo } from "../../../../types/Account";
import { jwtDecode } from "jwt-decode";
import "./profilePost.css";
import FavoriteBorderOutlinedIcon from "@mui/icons-material/FavoriteBorderOutlined";
import MapsUgcOutlinedIcon from "@mui/icons-material/MapsUgcOutlined";
import ShareOutlinedIcon from "@mui/icons-material/ShareOutlined";
import InsertEmoticonOutlinedIcon from "@mui/icons-material/InsertEmoticonOutlined";
import EmojiPicker from "emoji-picker-react";
import type { EmojiClickData } from "emoji-picker-react";

import MoreHorizOutlinedIcon from "@mui/icons-material/MoreHorizOutlined";
import CreatePost from "../create/createPost";
import SummaryBox from "../summary/summaryPost";
import ReportModal from "../report/reportModal";
import EditPost from "../create/editPost";
import ReactList from "../create/reactList";
import ChevronLeftOutlinedIcon from "@mui/icons-material/ChevronLeftOutlined";
import ChevronRightOutlinedIcon from "@mui/icons-material/ChevronRightOutlined";
import type { ReactType } from "../../../../types/Post";
import type { Comment } from "../../../../types/Post";
import { useNavigate } from "react-router-dom";
import { FollowButton } from "../relationship/follow";
import SharePostModal from "../create/sharePostModal";
import PostDetail from "../post/postDetail";
import ApproveModal from "../report/approveModal";
import { ToastService } from "../../../../services/ToastService";
import SaveToCollectionModal from "./SaveToCollectionModal";

interface ProfilePostProps {
  archive?: boolean;
  email?: string;
  listPostSearch?: any[]; // truyền trực tiếp danh sách post
}

const ListPost: React.FC<ProfilePostProps> = ({
  email,
  listPostSearch,
  archive,
}) => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [userInfoMap, setUserInfoMap] = useState<Record<string, UserInfo>>({});
  const [commentText, setCommentText] = useState<{ [key: string]: string }>({});
  const [activePost, setActivePost] = useState<Post | null>(null);
  const [isPostDetailOpen, setIsPostDetailOpen] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [openEmojiPicker, setOpenEmojiPicker] = useState<{
    type: "post" | "modal";
    postId?: string;
  } | null>(null);
  const [userReactMap, setUserReactMap] = useState<
    Record<string, "love" | "like" | "haha" | "wow" | "sad" | "angry" | null>
  >({});
  const [userCommentReactMap, setUserCommentReactMap] = useState<
    Record<string, "love" | "like" | "haha" | "wow" | "sad" | "angry" | null>
  >({});
  const [commentPopoverMap, setCommentPopoverMap] = useState<
    Record<string, boolean>
  >({});
  const [postPopoverMap, setPostPopoverMap] = useState<Record<string, boolean>>(
    {},
  );
  const [initializedReactMap, setInitializedReactMap] = useState(false);
  const [postMenuOpen, setPostMenuOpen] = useState<Record<string, boolean>>({});
  const menuRefs = useRef<Record<string, HTMLDivElement | null>>({});
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPost, setEditingPost] = useState<Post | null>(null);
  const [slideIndex, setSlideIndex] = useState<{ [key: string]: number }>({});
  const [isReactModalOpen, setReactModalOpen] = useState(false);
  const [selectedReactPost, setSelectedReactPost] = useState<Post | null>(null);
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);
  const [isApproveOpen, setIsApproveOpen] = useState(false);
  const [openSaveModal, setOpenSaveModal] = useState(false);
  const [selectedPostId, setSelectedPostId] = useState<string | null>(null);
  const [selectedReactComment, setSelectedReactComment] =
    useState<Comment | null>(null);
  const [reportPost, setReportPost] = useState<Post | null>(null);
  const [expandedPosts, setExpandedPosts] = useState<{
    [key: string]: boolean;
  }>({});
  const [openShareModal, setOpenShareModal] = useState(false);
  const [sharePost, setSharePost] = useState<Post | null>(null);
  const [showSummary, setShowSummary] = useState(false);
  const [summaryText, setSummaryText] = useState("");
  const [originalPostCache, setOriginalPostCache] = useState<
    Record<string, Post>
  >({});
  const [reloadFlag, setReloadFlag] = useState(false);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const sentinelRef = useRef<HTMLDivElement>(null);

  const defaultReact: ReactType = {
    love: [],
    like: [],
    haha: [],
    wow: [],
    sad: [],
    angry: [],
  };

  const token = localStorage.getItem("token");
  let currentUserEmail: string | null = email || null;
  let currentUserRole: string | null | null;
  let emailCheckUser: string | null | null;
  let roleCheckUser: string | null | null;

  if (!currentUserEmail && token) {
    try {
      interface JwtPayload {
        sub: string;
        role: string;
        exp: number;
        per: string;
      }
      const decoded: JwtPayload = jwtDecode<JwtPayload>(token);
      currentUserEmail = decoded.sub;
      currentUserRole = decoded.role;
    } catch (err) {
      console.error("❌ Token không hợp lệ:", err);
    }
  }

  if (token) {
    try {
      interface JwtPayload {
        sub: string;
        role: string;
        exp: number;
        per: string;
      }
      const decoded: JwtPayload = jwtDecode<JwtPayload>(token);
      emailCheckUser = decoded.sub;
      roleCheckUser = decoded.role;
    } catch (err) {
      console.error("❌ Token không hợp lệ:", err);
    }
  }

  const canComment = () => {
    const token = localStorage.getItem("token");
    if (!token) return false;

    try {
      const decoded: any = jwtDecode(token);
      return decoded.per?.[1] === "1";
    } catch {
      return false;
    }
  };

  const fetchPosts = async (isLoadMore = false) => {
    if (isLoadMore && (loading || !hasMore)) return;
    setLoading(true);
    try {
      let res;

      if (listPostSearch && listPostSearch.length > 0) {
        setPosts(listPostSearch);
        setLoading(false);
        return;
      }

      if (email) {
        res = await postAPI.getByEmail(email);
      } else if (archive) {
        res = await postAPI.getPostHidden();
      } else {
        res = await postAPI.getAll();
      }

      const newPosts: Post[] = res.post_list || [];

      if (isLoadMore) {
        setPosts((prev) => {
          const existingIds = new Set(prev.map((p) => p._id));
          const unique = newPosts.filter((p) => !existingIds.has(p._id));

          if (unique.length === 0) {
            setHasMore(false);
            return prev;
          }

          return [...prev, ...unique];
        });
      } else {
        setPosts(newPosts);
      }
    } catch (err) {
      console.error("❌ Lỗi fetch posts:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setHasMore(true);
    setPosts([]);
    fetchPosts();
  }, [email, listPostSearch, reloadFlag]);

  /* ---------- INFINITE SCROLL (only for main feed) ---------- */
  useEffect(() => {
    if (!hasMore || loading || email || archive || (listPostSearch && listPostSearch.length > 0)) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          fetchPosts(true);
        }
      },
      { threshold: 0.1 },
    );

    const el = sentinelRef.current;
    if (el) observer.observe(el);
    return () => observer.disconnect();
  }, [hasMore, loading, email, archive, listPostSearch]);

  useEffect(() => {
    if (!posts.length) return;

    const fetchAllUserInfo = async () => {
      const emailsSet = new Set<string>();
      posts.forEach((post) => {
        emailsSet.add(post.createdBy);
        post.comments?.forEach((cmt) => emailsSet.add(cmt.commentBy));
      });
      const emails = Array.from(emailsSet);

      const results = await Promise.all(
        emails.map(async (email) => {
          try {
            const res = await AccountService.get_account_info(email);
            return [email, res] as [string, UserInfo];
          } catch (err) {
            console.error("❌ Lỗi lấy user info:", email, err);
            return [email, null] as [string, UserInfo | null];
          }
        }),
      );

      const userMap: Record<string, UserInfo> = {};
      results.forEach(([email, info]) => {
        if (info) userMap[email] = info;
      });
      setUserInfoMap(userMap);
    };

    fetchAllUserInfo();
  }, [posts]);

  useEffect(() => {
    if (!posts.length || !currentUserEmail || initializedReactMap) return;

    const initialMap: Record<
      string,
      "love" | "like" | "haha" | "wow" | "sad" | "angry" | null
    > = {};
    const initialCommentMap: Record<
      string,
      "love" | "like" | "haha" | "wow" | "sad" | "angry" | null
    > = {};

    posts.forEach((post) => {
      const entry = post.react
        ? Object.entries(post.react).find(([_, users]) =>
            (users as string[]).includes(currentUserEmail!),
          )
        : null;

      initialMap[post._id] = entry ? (entry[0] as any) : null;

      post.comments?.forEach((cmt) => {
        const cmtEntry = cmt.reacts
          ? Object.entries(cmt.reacts).find(([_, users]) =>
              (users as string[]).includes(currentUserEmail!),
            )
          : null;

        initialCommentMap[cmt.commentId] = cmtEntry
          ? (cmtEntry[0] as any)
          : null;
      });
    });

    setUserReactMap(initialMap);
    setUserCommentReactMap(initialCommentMap);
    setInitializedReactMap(true);
  }, [posts, currentUserEmail, initializedReactMap]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const newState: Record<string, boolean> = {};
      let changed = false;

      Object.keys(menuRefs.current).forEach((postId) => {
        const ref = menuRefs.current[postId];
        if (ref && !ref.contains(e.target as Node)) {
          if (postMenuOpen[postId]) changed = true;
          newState[postId] = false;
        } else {
          newState[postId] = postMenuOpen[postId];
        }
      });

      if (changed) setPostMenuOpen(newState);
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [postMenuOpen]);

  const handleReact = async (
    postId: string,
    type: "love" | "like" | "haha" | "wow" | "sad" | "angry",
  ) => {
    try {
      const response = await postAPI.updateReact(postId, type);
      const updatedReact = response.react;
      setPosts((prev) =>
        prev.map((p) => (p._id === postId ? { ...p, react: updatedReact } : p)),
      );
      if (currentUserEmail) {
        const reactedEntry = Object.entries(updatedReact).find(([_, users]) =>
          (users as string[]).includes(currentUserEmail!),
        );
        setUserReactMap((prev) => ({
          ...prev,
          [postId]: reactedEntry ? (reactedEntry[0] as any) : null,
        }));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCommentReact = async (
    postId: string,
    commentId: string,
    type: "love" | "like" | "haha" | "wow" | "sad" | "angry",
  ) => {
    try {
      const response = await CommentService.updateCommentReact(
        postId,
        commentId,
        type,
      );
      const updatedReact = response.react;
      setPosts((prevPosts) =>
        prevPosts.map((post) => {
          if (post._id !== postId) return post;
          const updatedComments = post.comments?.map((cmt) =>
            cmt.commentId === commentId
              ? { ...cmt, reacts: updatedReact }
              : cmt,
          );
          return { ...post, comments: updatedComments };
        }),
      );
      const entry = currentUserEmail
        ? Object.entries(updatedReact).find(([_, users]) =>
            (users as string[]).includes(currentUserEmail!),
          )
        : null;
      setUserCommentReactMap((prev) => ({
        ...prev,
        [commentId]: entry ? (entry[0] as any) : null,
      }));
    } catch (err) {
      console.error("❌ Lỗi khi gửi reaction cho comment:", err);
    }
  };
  const getOriginalPost = async (postId: string) => {
    if (originalPostCache[postId]) return originalPostCache[postId];

    const res = await postAPI.getById(postId);
    const data = res.post;

    setOriginalPostCache((prev) => ({ ...prev, [postId]: data }));

    return data;
  };

  const handleAddComment = async (postId: string) => {
    // 🔒 CHECK QUYỀN BÌNH LUẬN
    const token = localStorage.getItem("token");
    if (token) {
      try {
        const decoded: any = jwtDecode(token);
        // per[1] === '0' → cấm comment
        if (decoded.per?.[1] === "0") {
          ToastService.error("Tài khoản của bạn đã bị cấm đăng tải bình luận");
          return;
        }
      } catch {
        ToastService.error(
          "Phiên đăng nhập không hợp lệ, vui lòng đăng nhập lại",
        );
        return;
      }
    }

    const newComment = commentText[postId]?.trim();
    if (!newComment) {
      ToastService.warning("Vui lòng nhập nội dung bình luận");
      return;
    }

    try {
      setOpenEmojiPicker(null);

      await CommentService.addComment({
        postId,
        content: newComment,
      });

      const updated = await postAPI.getById(postId);
      const updatedPost = updated.post || updated;

      setPosts((prev) => prev.map((p) => (p._id === postId ? updatedPost : p)));

      setActivePost(updatedPost);
      setCommentText((prev) => ({ ...prev, [postId]: "" }));
    } catch (err) {
      console.error(err);
      ToastService.error("Không thể thêm bình luận, vui lòng thử lại!");
    }
  };

  const handleEmojiClick = (postId: string, emojiData: EmojiClickData) => {
    setCommentText((prev) => ({
      ...prev,
      [postId]: (prev[postId] || "") + emojiData.emoji,
    }));
    setOpenEmojiPicker(null);
  };
  const openPostDetail = (post: Post) => {
    setActivePost(post);
    setIsPostDetailOpen(true);
    document.body.style.overflow = "hidden";
  };

  const closeCommentModal = () => {
    setShowModal(false);
    setActivePost(null);
    document.body.style.overflow = "auto";
  };
  const togglePostMenu = (postId: string) => {
    setPostMenuOpen((prev) => ({
      ...prev,
      [postId]: !prev[postId],
    }));
  };
  const handleEditPost = (post: Post) => {
    setEditingPost(post);
    setIsModalOpen(true);
    setPostMenuOpen((prev) => ({
      ...prev,
      [post._id]: false,
    }));
  };

  const handleDeletePost = async (postId: string) => {
    if (!postId) return;

    ToastService.confirm(
      "Bạn có chắc muốn xóa bài viết này?",
      async () => {
        try {
          await postAPI.deletePost(postId);

          ToastService.success("Xóa bài viết thành công!");

          setPosts((prev) => prev.filter((p) => p._id !== postId));
          setPostMenuOpen((prev) => ({ ...prev, [postId]: false }));
        } catch (err) {
          console.error("❌ Lỗi xóa bài viết:", err);
          ToastService.error("Xóa bài viết thất bại, vui lòng thử lại!");
        }
      },
      {
        confirmText: "Xóa",
        cancelText: "Hủy",
      },
    );
  };

  const handleSummary = async (postId: string) => {
    console.log("CLICK SUMMARY");

    if (!postId) return;

    try {
      // 1️⃣ Gọi API AI để tạo summary
      await aiAPI.summarizePost(postId);

      // 2️⃣ Lấy lại post mới nhất
      const res = await postAPI.getById(postId);
      const data = res.post;

      // 3️⃣ Cache post
      setOriginalPostCache((prev) => ({
        ...prev,
        [postId]: data,
      }));

      console.log("AI Summary:", data.ai_summary);

      // 4️⃣ Hiển thị summary
      setSummaryText(data.ai_summary || "Không có tóm tắt.");
      setShowSummary(true);
    } catch (err) {
      console.error("AI summary error:", err);
      setSummaryText("Không thể tóm tắt bài đăng.");
      setShowSummary(true);
    }
  };
  const getIndex = (postId: string) => slideIndex[postId] ?? 0;

  const handleNext = (postId: string, total: number) => {
    setSlideIndex((prev) => ({
      ...prev,
      [postId]: (getIndex(postId) + 1) % total,
    }));
  };

  const handlePrev = (postId: string, total: number) => {
    setSlideIndex((prev) => ({
      ...prev,
      [postId]: (getIndex(postId) - 1 + total) % total,
    }));
  };
  const navigate = useNavigate();

  const goToProfile = (email: string) => {
    navigate(`/profile/${email}`);
  };
  const handleReport = (post: Post) => {
    setPostMenuOpen((prev) => ({ ...prev, [post._id]: false }));

    requestAnimationFrame(() => setReportPost(post));
  };

  const truncateWords = (text: string, limit: number) => {
    const words = text.split(" ");
    if (words.length <= limit) return text;
    return words.slice(0, limit).join(" ") + "...";
  };

  const handleShared = () => {
    setReloadFlag((prev) => !prev);
  };

  const handleRemove = (post: Post) => {
    // đóng menu
    setPostMenuOpen((prev) => ({ ...prev, [post._id]: false }));

    // dùng requestAnimationFrame để chắc chắn render cập nhật
    requestAnimationFrame(() => {
      setSelectedPost(post); // lưu bài viết đang gỡ
      setIsApproveOpen(true); // mở modal
    });
  };

  const handleBlock = async (ownerEmail: string) => {
    if (!emailCheckUser) return;

    try {
      await AccountService.block({
        owner: emailCheckUser,
        client: ownerEmail,
      });

      console.log("Đã chặn:", emailCheckUser, ownerEmail);

      // 👉 Nếu bạn muốn update UI sau khi chặn:
      setUserInfoMap((prev) => ({
        ...prev,
        [ownerEmail]: {
          ...prev[ownerEmail],
          isBlocked: true,
        },
      }));
      navigate("/home");
      ToastService.success("Chặn thành công");
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } catch (err) {
      console.error("Block failed:", err);
    }
  };

  const refreshPost = async (postId: string) => {
    const updated = await postAPI.getById(postId);
    const updatedPost = updated.post || updated;

    setPosts((prev) => prev.map((p) => (p._id === postId ? updatedPost : p)));
    setActivePost(updatedPost);
  };

  const handleSaved = (post: any) => {
    setSelectedPostId(post._id);
    setOpenSaveModal(true);
    ToastService.success("Chọn bộ sưu tập để lưu bài viết");
  };

  const handleRemovePostLocal = (postId: string) => {
    setPosts((prev) => prev.filter((p) => p._id !== postId));
  };

  const getFileType = (filename: string) => {
    const ext = filename.split(".").pop()?.toLowerCase();

    if (["jpg", "jpeg", "png", "gif", "webp"].includes(ext || "")) {
      return "image";
    }

    if (["mp4", "webm", "ogg"].includes(ext || "")) {
      return "video";
    }

    return "file";
  };

  function formatTimeVN(dateString: string) {
    const utcDate = new Date(dateString + "Z");

    // Giờ Việt Nam = UTC + 7
    const vnDate = new Date(utcDate.getTime() + 7 * 60 * 60 * 1000);
    const nowVN = new Date(Date.now() + 7 * 60 * 60 * 1000);

    const diffMs = nowVN.getTime() - vnDate.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMinutes < 1) return "vừa xong";
    if (diffMinutes < 60) return `${diffMinutes} phút trước`;
    if (diffHours < 24) return `${diffHours} giờ trước`;
    if (diffDays < 3) return `${diffDays} ngày trước`;

    return vnDate.toLocaleString("vi-VN");
  }

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
    <div className="profilePost">
      <div className="postSection">
        {posts.map((post) => {
          const isShare = post.postType === "share";
          let originalPost =
            isShare && post.postId
              ? posts.find((p) => p._id === post.postId) ||
                originalPostCache[post.postId] ||
                null
              : null;

          if (isShare && post.postId && !originalPost) {
            getOriginalPost(post.postId);
          }
          const commentCount = post.comments?.length ?? 0;

          const fileList = (post.thumbnails ?? []).filter(
            (name: string) => getFileType(name) === "file",
          );
          const mediaItems = (post.thumbnails || [])
            .map((fileId, idx) => {
              const url = post.thumbnails_url?.[idx];
              return { fileId, url };
            })
            .filter((item) =>
              /\.(jpg|jpeg|png|gif|webp|mp4|mov|avi)$/i.test(item.fileId),
            );
          return (
            <div className="post" key={post._id}>
              <div className="postInfo" style={{ cursor: "pointer" }}>
                <img
                  className="postInfoImg"
                  src={userInfoMap[post.createdBy]?.avatar || ""}
                  alt="avatar"
                  onClick={() => goToProfile(post.createdBy)}
                />
                <div className="postInfoText">
                  <div
                    className="postInfoName"
                    onClick={() => goToProfile(post.createdBy)}
                  >
                    {userInfoMap[post.createdBy]?.fullName || post.createdBy}
                  </div>
                  <div className="timingInfo">
                    • {post.createdAt ? formatTimeVN(post.createdAt) : ""}
                  </div>
                </div>

                <div className="follow-check">
                  {post.createdBy !== currentUserEmail &&
                    !userInfoMap[post.createdBy]?.followers?.includes(
                      currentUserEmail || "",
                    ) && (
                      <FollowButton
                        ownerEmail={currentUserEmail!}
                        clientEmail={post.createdBy}
                        onFollowSuccess={() => {
                          setUserInfoMap((prev) => ({
                            ...prev,
                            [post.createdBy]: {
                              ...prev[post.createdBy],
                              followers: [
                                ...(prev[post.createdBy]?.followers ?? []),
                                currentUserEmail!,
                              ],
                            },
                          }));
                        }}
                      />
                    )}
                </div>

                <button
                  className="optionPost"
                  onClick={(e) => {
                    e.stopPropagation();
                    togglePostMenu(post._id);
                  }}
                >
                  <MoreHorizOutlinedIcon />
                </button>

                <div
                  className="postMenu"
                  ref={(el) => {
                    menuRefs.current[post._id] = el;
                  }}
                >
                  {postMenuOpen[post._id] && (
                    <div className="menuDropdown">
                      {post.createdBy === emailCheckUser ? (
                        <>
                          <div
                            className="menuItem"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEditPost(post);
                            }}
                          >
                            ✏️ Chỉnh sửa bài đăng
                          </div>

                          <div
                            className="menuItem"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleSummary(post._id);
                            }}
                          >
                            Tóm tắt bài đăng
                          </div>

                          <div
                            className="menuItem delete"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeletePost(post._id);
                            }}
                          >
                            🗑️ Xóa bài đăng
                          </div>
                        </>
                      ) : (
                        <>
                          {/* Người khác nhưng không phải moderator */}
                          {roleCheckUser !== "Moderator" && (
                            <div
                              className="menuItem"
                              onClick={() => handleReport(post)}
                            >
                              🚩 Tố cáo bài viết
                            </div>
                          )}
                          <div
                            className="menuItem"
                            onClick={() => handleSaved(post)}
                          >
                            🔖 Lưu bài viết
                          </div>

                          {/* Nếu currentUser là Moderator → thêm Gỡ bài viết */}
                          {roleCheckUser === "Moderator" && (
                            <div
                              className="menuItem delete"
                              onClick={() => handleRemove(post)}
                            >
                              🛑 Gỡ bài viết
                            </div>
                          )}

                          <div
                            className="menuItem block"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleBlock(post.createdBy);
                              setPostMenuOpen((prev) => ({
                                ...prev,
                                [post._id]: false,
                              }));
                            }}
                          >
                            ⛔ Chặn
                          </div>
                        </>
                      )}
                    </div>
                  )}
                </div>
              </div>
              <div className="postTitle">
                <span>{post.title}</span>
              </div>

              <div className="postContent">
                <p>
                  {expandedPosts[post._id]
                    ? post.content
                    : truncateWords(post.content, 100)}
                </p>

                {post.content.split(" ").length > 100 && (
                  <button
                    className="toggleReadMore"
                    onClick={() =>
                      setExpandedPosts((prev) => ({
                        ...prev,
                        [post._id]: !prev[post._id],
                      }))
                    }
                  >
                    {expandedPosts[post._id] ? "Thu gọn" : "Xem thêm"}
                  </button>
                )}

                {/* 🔥 FILE DOWNLOAD SECTION */}
                {fileList.length > 0 && (
                  <div className="fileList">
                    {fileList.map((name: string, index: number) => {
                      const thumbnails = post.thumbnails ?? [];
                      const thumbnailsUrl = post.thumbnails_url ?? [];

                      const displayName = name.split("_").slice(1).join("_");

                      const url = thumbnailsUrl[thumbnails.indexOf(name)];

                      return (
                        <a key={index} href={url} download className="fileItem">
                          <div className="fileIcon">📄</div>

                          <div className="fileInfo">
                            <div className="fileName">{displayName}</div>
                          </div>
                        </a>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* share bai */}
              {isShare && originalPost && (
                <div
                  className="post sharedPost"
                  onClick={(e) => {
                    e.stopPropagation();
                    openPostDetail(originalPost);
                  }}
                >
                  {originalPost.thumbnails_url &&
                    originalPost.thumbnails_url.length > 0 && (
                      <div className="postImg">
                        <div
                          className="postSlider"
                          style={{
                            transform: `translateX(-${
                              getIndex(originalPost._id) * 100
                            }%)`,
                          }}
                        >
                          {originalPost.thumbnails_url.map((url, idx) => {
                            const fileName =
                              originalPost.thumbnails?.[idx] || "";
                            return (
                              <div className="slide" key={idx}>
                                {/\.mp4|\.mov$/i.test(fileName) ? (
                                  <video className="postVideo" controls>
                                    <source src={url} type="video/mp4" />
                                  </video>
                                ) : (
                                  <img className="postImage" src={url} alt="" />
                                )}
                              </div>
                            );
                          })}
                        </div>

                        {originalPost.thumbnails_url.length > 1 && (
                          <>
                            {getIndex(originalPost._id) > 0 && (
                              <ChevronLeftOutlinedIcon
                                className="nav-left"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handlePrev(
                                    originalPost._id,
                                    originalPost.thumbnails_url.length,
                                  );
                                }}
                              />
                            )}

                            {getIndex(originalPost._id) <
                              originalPost.thumbnails_url.length - 1 && (
                              <ChevronRightOutlinedIcon
                                className="nav-right"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleNext(
                                    originalPost._id,
                                    originalPost.thumbnails_url.length,
                                  );
                                }}
                              />
                            )}

                            <div className="dots-post">
                              {originalPost.thumbnails_url.map((_, idx) => (
                                <span
                                  key={idx}
                                  className={`dot-post ${
                                    idx === getIndex(originalPost._id)
                                      ? "active"
                                      : ""
                                  }`}
                                  onClick={() =>
                                    setSlideIndex((prev) => ({
                                      ...prev,
                                      [originalPost._id]: idx,
                                    }))
                                  }
                                ></span>
                              ))}
                            </div>
                          </>
                        )}
                      </div>
                    )}
                  <div
                    className="postInfo"
                    style={{ cursor: "pointer", marginTop: "10px" }}
                  >
                    <img
                      className="postInfoImg"
                      src={userInfoMap[originalPost.createdBy]?.avatar || ""}
                      alt="avatar"
                      onClick={() => goToProfile(originalPost.createdBy)}
                    />
                    <div
                      className="postInfoName"
                      onClick={() => goToProfile(originalPost.createdBy)}
                    >
                      {userInfoMap[originalPost.createdBy]?.fullName
                        ? userInfoMap[originalPost.createdBy].fullName
                        : (() => {
                            // Nếu chưa có fullName, gọi API lấy thông tin user
                            AccountService.get_account_info(
                              originalPost.createdBy,
                            )
                              .then((info) => {
                                if (info) {
                                  setUserInfoMap((prev) => ({
                                    ...prev,
                                    [originalPost.createdBy]: info,
                                  }));
                                }
                              })
                              .catch((err) =>
                                console.error(
                                  "❌ Lỗi lấy thông tin user gốc:",
                                  err,
                                ),
                              );
                            // Khi đang load hiển thị email tạm thời
                            return originalPost.createdBy;
                          })()}
                    </div>
                    <div className="timingInfo">
                      •{" "}
                      {originalPost.createdAt
                        ? new Date(originalPost.createdAt).toLocaleString(
                            "vi-VN",
                          )
                        : ""}
                    </div>
                  </div>
                  <div className="postTitle">
                    <span>{originalPost.title}</span>
                  </div>

                  <div className="postContent">
                    <p>
                      {expandedPosts[originalPost._id]
                        ? originalPost.content
                        : truncateWords(originalPost.content, 100)}
                    </p>
                    {originalPost.content.split(" ").length > 100 && (
                      <button
                        className="toggleReadMore"
                        onClick={() =>
                          setExpandedPosts((prev) => ({
                            ...prev,
                            [originalPost._id]: !prev[originalPost._id],
                          }))
                        }
                      >
                        {expandedPosts[originalPost._id]
                          ? "Thu gọn"
                          : "Xem thêm"}
                      </button>
                    )}
                  </div>
                </div>
              )}

              {mediaItems.length > 0 && (
                <div
                  className="postImg"
                  onClick={(e) => {
                    e.stopPropagation();
                    openPostDetail(post);
                  }}
                >
                  <div
                    className="postSlider"
                    style={{
                      transform: `translateX(-${getIndex(post._id) * 100}%)`,
                    }}
                  >
                    {mediaItems.map((item, idx) => (
                      <div className="slide" key={idx}>
                        {/\.(mp4|mov|avi)$/i.test(item.fileId) ? (
                          <video className="postVideo" controls>
                            <source src={item.url} />
                          </video>
                        ) : (
                          <img className="postImage" src={item.url} alt="" />
                        )}
                      </div>
                    ))}
                  </div>

                  {/* NAV */}
                  {mediaItems.length > 1 && (
                    <>
                      {getIndex(post._id) > 0 && (
                        <ChevronLeftOutlinedIcon
                          className="nav-left"
                          onClick={(e) => {
                            e.stopPropagation();
                            handlePrev(post._id, mediaItems.length);
                          }}
                        />
                      )}

                      {getIndex(post._id) < mediaItems.length - 1 && (
                        <ChevronRightOutlinedIcon
                          className="nav-right"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleNext(post._id, mediaItems.length);
                          }}
                        />
                      )}
                    </>
                  )}

                  {/* DOTS */}
                  {mediaItems.length > 1 && (
                    <div className="dots-post">
                      {mediaItems.map((_, idx) => (
                        <span
                          key={idx}
                          className={`dot-post ${
                            idx === getIndex(post._id) ? "active" : ""
                          }`}
                        />
                      ))}
                    </div>
                  )}
                </div>
              )}

              <div className="iconBlock">
                <div className="leftIcon">
                  <div
                    className="like-container"
                    onMouseEnter={(e) => {
                      e.stopPropagation();
                      setPostPopoverMap((prev) => ({
                        ...prev,
                        [post._id]: true,
                      }));
                    }}
                    onMouseLeave={(e) => {
                      e.stopPropagation();
                      setPostPopoverMap((prev) => ({
                        ...prev,
                        [post._id]: false,
                      }));
                    }}
                  >
                    <button
                      className={`react-btn ${
                        userReactMap[post._id]
                          ? `active-${userReactMap[post._id]}`
                          : ""
                      }`}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleReact(post._id, "love");
                      }}
                    >
                      {userReactMap[post._id] === "love" ? (
                        "❤️"
                      ) : userReactMap[post._id] === "like" ? (
                        "👍"
                      ) : userReactMap[post._id] === "haha" ? (
                        "😂"
                      ) : userReactMap[post._id] === "wow" ? (
                        "😮"
                      ) : userReactMap[post._id] === "sad" ? (
                        "😢"
                      ) : userReactMap[post._id] === "angry" ? (
                        "😡"
                      ) : (
                        <FavoriteBorderOutlinedIcon />
                      )}
                    </button>

                    {postPopoverMap[post._id] && (
                      <div
                        className="emote-popover"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <span onClick={() => handleReact(post._id, "love")}>
                          ❤️
                        </span>
                        <span onClick={() => handleReact(post._id, "like")}>
                          👍
                        </span>
                        <span onClick={() => handleReact(post._id, "haha")}>
                          😂
                        </span>
                        <span onClick={() => handleReact(post._id, "wow")}>
                          😮
                        </span>
                        <span onClick={() => handleReact(post._id, "sad")}>
                          😢
                        </span>
                        <span onClick={() => handleReact(post._id, "angry")}>
                          😡
                        </span>
                      </div>
                    )}
                  </div>

                  <MapsUgcOutlinedIcon
                    sx={{
                      fontSize: "23px",
                      marginLeft: "8px",
                      cursor: "pointer",
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      openPostDetail(post);
                      console.log("bấm", post);
                    }}
                  />

                  {post.createdBy !== emailCheckUser && (
                    <ShareOutlinedIcon
                      sx={{
                        fontSize: "23px",
                        marginLeft: "8px",
                        cursor: "pointer",
                      }}
                      onClick={() => {
                        setSharePost(post);
                        setOpenShareModal(true);
                      }}
                    />
                  )}
                </div>
              </div>

              {Object.values(post.react || {}).reduce(
                (s, arr) => s + arr.length,
                0,
              ) > 0 && (
                <label
                  className="countReact-Post"
                  onClick={() => {
                    setSelectedReactPost(post);
                    setReactModalOpen(true);
                  }}
                >
                  {Object.values(post.react || {}).reduce(
                    (s, arr) => s + arr.length,
                    0,
                  )}{" "}
                  lượt bày tỏ cảm xúc
                </label>
              )}

              <div
                className="commentSection"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="commentInput">
                  <textarea
                    value={commentText[post._id] || ""}
                    onChange={(e) => {
                      const value = e.target.value;
                      setCommentText((prev) => ({
                        ...prev,
                        [post._id]: value,
                      }));
                      e.target.style.height = "auto";
                      e.target.style.height = `${e.target.scrollHeight}px`;
                    }}
                    placeholder={
                      commentCount > 0
                        ? `Đã có ${commentCount} bình luận về bài viết này, bạn là người tiếp theo?`
                        : "Hãy là người bình luận đầu tiên!"
                    }
                    className="commentBox"
                    rows={1}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        if (post._id) handleAddComment(post._id);
                      }
                    }}
                  />
                  <div className="emojiWrapper">
                    <InsertEmoticonOutlinedIcon
                      sx={{ fontSize: 22, color: "#777", cursor: "pointer" }}
                      onClick={(e) => {
                        e.stopPropagation();
                        setOpenEmojiPicker((prev) =>
                          prev?.type === "post" && prev.postId === post._id
                            ? null
                            : { type: "post", postId: post._id },
                        );
                      }}
                    />
                    {openEmojiPicker?.type === "post" &&
                      openEmojiPicker.postId === post._id && (
                        <div className="emojiPickerContainer">
                          <EmojiPicker
                            onEmojiClick={(emojiData) =>
                              handleEmojiClick(post._id, emojiData)
                            }
                          />
                        </div>
                      )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}

        {/* Sentinel: trigger load more khi scroll đến cuối */}
        {!email && !archive && !listPostSearch?.length && (
          <div ref={sentinelRef} style={{ height: 1 }}>
            {loading && hasMore && (
              <p style={{ textAlign: "center", padding: "16px 0", color: "#888" }}>
                Đang tải thêm bài viết...
              </p>
            )}
          </div>
        )}

        {/* Đã xem hết tất cả bài viết */}
        {!hasMore && !email && !archive && !listPostSearch?.length && (
          <div className="end-of-feed">
            <p>Bạn đã xem hết tất cả bài viết</p>
            <span
              className="back-to-top"
              onClick={() => {
                const container = document.querySelector(".main-right-side");
                if (container) {
                  container.scrollTo({ top: 0, behavior: "smooth" });
                }
              }}
            >
              Quay lại trang đầu
            </span>
          </div>
        )}

        {isPostDetailOpen && activePost && (
          <PostDetail
            activePost={activePost}
            onClose={() => setIsPostDetailOpen(false)}
            onCommentAdded={refreshPost}
            onOpenOriginalPost={openOriginalPost}
            onPostDeleted={(postId: string) => {
              setPosts((prev) => prev.filter((p) => p._id !== postId));
              setIsPostDetailOpen(false); // đóng modal nếu xóa post
            }}
            onActivePostUpdate={(updatedPost: Post) => {
              setActivePost(updatedPost); // cập nhật lại post sau khi edit
            }}
          />
        )}

        <CreatePost
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false);
            setEditingPost(null);
          }}
          editingPost={editingPost}
          onPostSaved={fetchPosts}
        />
        <EditPost
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false);
            setEditingPost(null);
          }}
          post={editingPost}
          onPostUpdated={fetchPosts}
        />
        <ReportModal
          isOpen={!!reportPost}
          onClose={() => setReportPost(null)}
          policy_type="bài đăng"
          type="post"
          violatorEmail={reportPost?.createdBy}
          content={reportPost?.content || ""}
          contentId={reportPost?._id}
          contentParentId=""
        />
        {selectedPost && (
          <ApproveModal
            isOpen={isApproveOpen}
            onClose={() => setIsApproveOpen(false)}
            policy_element="bài đăng"
            element="post"
            elementId={selectedPost._id}
            currentUserEmail={currentUserEmail ?? ""}
            post={selectedPost} // <- truyền bài viết vào modal
            onRemoved={() => handleRemovePostLocal(selectedPost._id)}
          />
        )}

        {selectedReactPost && (
          <ReactList
            isOpen={isReactModalOpen}
            onClose={() => setReactModalOpen(false)}
            reacts={selectedReactPost.react ?? defaultReact}
            userInfoMap={userInfoMap}
          />
        )}
        {selectedReactComment && (
          <ReactList
            isOpen={isReactModalOpen}
            onClose={() => setReactModalOpen(false)}
            reacts={selectedReactComment.reacts ?? defaultReact}
            userInfoMap={userInfoMap}
          />
        )}
        <SharePostModal
          isOpen={openShareModal}
          onClose={() => setOpenShareModal(false)}
          postId={sharePost?._id || ""}
          onShared={handleShared} // 👈 thêm dòng này
        />
        {showSummary && (
          <SummaryBox
            summary={summaryText}
            onClose={() => setShowSummary(false)}
          />
        )}
        {openSaveModal && selectedPostId && (
          <SaveToCollectionModal
            postId={selectedPostId}
            email={currentUserEmail!}
            onClose={() => {
              setOpenSaveModal(false);
              setSelectedPostId(null);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default ListPost;
