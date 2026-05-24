import React, { useEffect, useState, useRef } from "react";
import { postAPI } from "../../../../services/PostService";
import AccountService from "../../../../services/AccountService";
import CommentService from "../../../../services/CommentService";
import FileService from "../../../../services/FileService";
import type { Post } from "../../../../types/Post";
import type { UserInfo } from "../../../../types/Account";
import { jwtDecode } from "jwt-decode";
import "../profile/profilePost.css";
import FavoriteBorderOutlinedIcon from "@mui/icons-material/FavoriteBorderOutlined";
import ShareOutlinedIcon from "@mui/icons-material/ShareOutlined";
import InsertEmoticonOutlinedIcon from "@mui/icons-material/InsertEmoticonOutlined";
import EmojiPicker from "emoji-picker-react";
import type { EmojiClickData } from "emoji-picker-react";
import { motion, AnimatePresence } from "framer-motion";
import ApproveModal from "../report/approveModal";
import MoreHorizOutlinedIcon from "@mui/icons-material/MoreHorizOutlined";
import ReactList from "../create/reactList";
import ChevronLeftOutlinedIcon from "@mui/icons-material/ChevronLeftOutlined";
import ChevronRightOutlinedIcon from "@mui/icons-material/ChevronRightOutlined";
import type { ReactType } from "../../../../types/Post";
import type { Comment } from "../../../../types/Post";
import { useNavigate } from "react-router-dom";
import SharePostModal from "../create/sharePostModal";
import EditPost from "../create/editPost";
import ReportModal from "../report/reportModal";
import { ToastService } from "../../../../services/ToastService";
import AddToPhotosIcon from "@mui/icons-material/AddToPhotos";
import ReplyComment from "./replyComment";
import type { CommentReply } from "../../../../types/CommentReply";
import CloseOutlinedIcon from "@mui/icons-material/CloseOutlined";

interface DetailPostProps {
  activePost: Post;
  focusCommentId?: string | null;
  onClose: () => void;
  onCommentAdded: (postId: string) => void;
  onOpenOriginalPost: (postId: string) => void;
  onPostDeleted?: (postId: string) => void; // ← thêm dòng này
  onActivePostUpdate?: (post: Post) => void;
}

const PostDetail: React.FC<DetailPostProps> = ({
  activePost,
  onClose,
  onCommentAdded,
  focusCommentId,
  onOpenOriginalPost,
  onPostDeleted, // ← nhận prop mới
  onActivePostUpdate,
}) => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [userInfoMap, setUserInfoMap] = useState<Record<string, UserInfo>>({});
  const [commentText, setCommentText] = useState<{ [key: string]: string }>({});
  const commentListRef = useRef<HTMLDivElement>(null);
  const [openCommentMenu, setOpenCommentMenu] = useState<
    Record<string, boolean>
  >({});
  const [reportComment, setReportComment] = useState<any | null>(null);
  const [reportModalOpen, setReportModalOpen] = useState(false);

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
  const [slideIndex, setSlideIndex] = useState<{ [key: string]: number }>({});
  const [isReactModalOpen, setReactModalOpen] = useState(false);
  const [selectedReactPost, setSelectedReactPost] = useState<Post | null>(null);
  const [selectedComment, setSelectedComment] = useState<Comment | null>(null);
  const [editingPost, setEditingPost] = useState<Post | null>(null);
  const [isApproveOpen, setIsApproveOpen] = useState(false);
  const commentInputRef = useRef<HTMLTextAreaElement | null>(null);
  const [selectedReactComment, setSelectedReactComment] =
    useState<Comment | null>(null);
  const [reportPost, setReportPost] = useState<Post | null>(null);
  const [expandedPosts, setExpandedPosts] = useState<{
    [key: string]: boolean;
  }>({});
  const [openShareModal, setOpenShareModal] = useState(false);
  const [sharePost, setSharePost] = useState<Post | null>(null);
  const [reloadFlag, setReloadFlag] = useState(false);
  const hasFocusedRef = useRef(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);
  const [commentFiles, setCommentFiles] = useState<File[]>([]);

  type PreviewFile = {
    url: string;
    type: "image" | "video" | "file";
    name: string;
  };

  const [previewUrls, setPreviewUrls] = useState<PreviewFile[]>([]);
  const [replyingTo, setReplyingTo] = useState<any>(null);
  const [replyCountMap, setReplyCountMap] = useState<Record<string, number>>(
    {},
  );

  const [openReplyMap, setOpenReplyMap] = useState<Record<string, boolean>>({});
  const [newReply, setNewReply] = useState<Record<string, CommentReply>>({});
  const [userList, setUserList] = useState<any[]>([]);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [mentionRange, setMentionRange] = useState<{
    start: number;
    end: number;
  } | null>(null);

  const defaultReact: ReactType = {
    love: [],
    like: [],
    haha: [],
    wow: [],
    sad: [],
    angry: [],
  };

  const token = localStorage.getItem("token");
  let currentUserEmail: string | null = null;
  let currentUserRole: string | null = null;

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
      currentUserRole = decoded.role;
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

  const fetchPosts = async () => {
    try {
      console.log("hhhhhhhhh", activePost);
      let res;
      console.log("aaaaaaaaaaaaaa:", activePost.createdBy);
      if (activePost.createdBy) {
        res = await postAPI.getByEmail(activePost.createdBy);
      } else {
        res = await postAPI.getAll();
      }

      console.log("yyyyyyyyyyyyyyyyyyy:", res);
      setPosts(res.post_list || []);
    } catch (err) {
      console.error("❌ Lỗi fetch posts:", err);
    }
  };

  useEffect(() => {
    fetchPosts();
  }, [activePost.createdBy, reloadFlag]);

  useEffect(() => {
    console.log("cccccccccccccc...");
    if (!posts.length) return;

    const fetchAllUserInfo = async () => {
      const emailsSet = new Set<string>();
      posts.forEach((post) => {
        emailsSet.add(post.createdBy);
        console.log("✅ Lấy user info thành công:", emailsSet);
        post.comments?.forEach((cmt) => emailsSet.add(cmt.commentBy));
      });
      const emails = Array.from(emailsSet);

      const results = await Promise.all(
        emails.map(async (email) => {
          try {
            const res = await AccountService.get_account_info(email);
            console.log("✅ Lấy user info thành công:", email, res);
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
    if (!focusCommentId) return;
    if (!activePost?.comments?.length) return;
    if (hasFocusedRef.current) return;

    const el = document.getElementById(`comment-${focusCommentId}`);
    if (el) {
      el.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });

      el.classList.add("highlight-comment");
      setTimeout(() => {
        el.classList.remove("highlight-comment");
      }, 2000);

      hasFocusedRef.current = true; // ✅ chỉ focus 1 lần
    }
  }, [focusCommentId, activePost.comments]);

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

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const relation = await AccountService.get_account_relation(
          currentUserEmail!,
        );
        const emails = relation.followed || [];

        const users = await Promise.all(
          emails.map((email) => AccountService.get_account_info(email)),
        );

        const mapped = users.map((u) => ({
          id: u.email,
          name: u.fullName || u.username || u.email,
          avatar: u.avatar,
        }));

        setUserList(mapped);
      } catch (err) {
        console.error(err);
      }
    };

    if (currentUserEmail) fetchUsers();
  }, [currentUserEmail]);

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

      if (activePost && activePost._id === postId) {
        const updatedComments = activePost.comments?.map((cmt) =>
          cmt.commentId === commentId ? { ...cmt, reacts: updatedReact } : cmt,
        );
        onCommentAdded("");
        Object.assign(activePost, { comments: updatedComments });
      }
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

  const handleAddComment = async (postId: string) => {
    if (!canComment()) {
      ToastService.error("Tài khoản của bạn đã bị cấm đăng tải bình luận");
      return;
    }

    const newComment = commentText[postId]?.trim();

    // ✅ cho phép chỉ gửi ảnh/video
    if (!newComment && commentFiles.length === 0) {
      ToastService.warning("Vui lòng nhập nội dung hoặc chọn ảnh/video");
      return;
    }

    try {
      setOpenEmojiPicker(null);

      // 🔥 upload file nếu có
      let uploadedUrls: string[] = [];
      if (commentFiles.length > 0) {
        uploadedUrls = await uploadFiles(commentFiles);
      }

      if (replyingTo) {
        const payload: any = {
          postId,
          content: newComment || "",
          thumbnails: uploadedUrls, // 👈 thêm vào đây
        };

        if (replyingTo.path && replyingTo.path.length > 0) {
          payload.path = replyingTo.path;
        } else {
          payload.parentId = replyingTo.commentId;
        }

        const res = await CommentService.addCommentReply(payload);
        const newReply = res.comment;

        const rootId = replyingTo.parentId || replyingTo.commentId;

        setNewReply((prev) => ({
          ...prev,
          [rootId]: newReply,
        }));

        setReplyCountMap((prev) => ({
          ...prev,
          [rootId]: (prev[rootId] || 0) + 1,
        }));

        setOpenReplyMap((prev) => ({
          ...prev,
          [rootId]: true,
        }));
      } else {
        // 👉 COMMENT THƯỜNG
        await CommentService.addComment({
          postId,
          content: newComment || "",
          thumbnails: uploadedUrls,
        });

        onCommentAdded(activePost._id);
      }

      // scroll xuống cuối
      setTimeout(() => {
        if (commentListRef.current) {
          commentListRef.current.scrollTop =
            commentListRef.current.scrollHeight;
        }
      }, 50);

      // update lại post
      const updated = await postAPI.getById(postId);
      const updatedPost = updated.post || updated;
      setPosts((prev) => prev.map((p) => (p._id === postId ? updatedPost : p)));

      // reset input + file
      setCommentText((prev) => ({ ...prev, [postId]: "" }));
      setCommentFiles([]); // 🔥 QUAN TRỌNG
      setPreviewUrls([]);
      // reset reply
      setReplyingTo(null);
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

  const togglePostMenu = (postId: string) => {
    setPostMenuOpen((prev) => ({
      ...prev,
      [postId]: !prev[postId],
    }));
  };

  const handleDeleteComment = async (postId: string, commentId: string) => {
    try {
      await CommentService.updateCommentStatus(postId, {
        commentId,
        statusComment: "hidden",
      });

      // ✅ 1. Cập nhật posts
      setPosts((prevPosts) =>
        prevPosts.map((post) => {
          if (post._id !== postId) return post;
          return {
            ...post,
            comments: post.comments?.filter(
              (cmt) => cmt.commentId !== commentId,
            ),
          };
        }),
      );

      // ✅ 2. Cập nhật activePost (QUAN TRỌNG)
      if (activePost && activePost._id === postId) {
        const updatedComments = activePost.comments?.filter(
          (cmt) => cmt.commentId !== commentId,
        );

        Object.assign(activePost, { comments: updatedComments });
        onCommentAdded(""); // ép re-render modal
      }
    } catch (error) {
      ToastService.error("Không thể xóa bình luận, vui lòng thử lại!");
    }
  };
  const fetchReplyCount = async (commentId: string, postId: string) => {
    try {
      const data = { postId, parentId: commentId };
      const res = await CommentService.getCommentReply(data);
      console.log("truyen vao:", postId, commentId, res);
      console.log(
        `Số reply cho comment ${commentId}:`,
        res.commentReplys?.length || 0,
      );

      setReplyCountMap((prev) => ({
        ...prev,
        [commentId]: res.commentReplys?.length || 0,
      }));
    } catch (err) {
      console.error("Lỗi khi lấy số reply:", err);
      setReplyCountMap((prev) => ({ ...prev, [commentId]: 0 }));
    }
  };
  useEffect(() => {
    if (activePost?.comments) {
      activePost.comments.forEach((comment) => {
        fetchReplyCount(comment.commentId, activePost._id);
      });
    }
  }, [activePost]);

  useEffect(() => {
    resetTextareaHeight();
  }, [previewUrls]);

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
    // Gọi callback onClose từ cha để đóng modal
    onClose?.();
    // Chuyển sang trang profile
    navigate(`/profile/${email}`);
  };

  const handleReport = (post: Post) => {
    console.log("Report post:", post);
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

  const handleBlock = async (ownerEmail: string) => {
    if (!currentUserEmail) return;

    console.log("Blocking user:", currentUserEmail, ownerEmail);

    try {
      await AccountService.block({
        owner: currentUserEmail,
        client: ownerEmail,
      });

      console.log("Đã chặn:", ownerEmail);

      // Cập nhật state nếu cần (optional)
      setUserInfoMap((prev) => ({
        ...prev,
        [ownerEmail]: {
          ...prev[ownerEmail],
          isBlocked: true,
        },
      }));

      // Hiển thị toast trước khi reload
      ToastService.success("Người dùng đã bị chặn");

      setTimeout(() => {
        window.location.reload();
      }, 500);
      navigate("/home");
    } catch (err) {
      console.error("Block failed:", err);
      ToastService.error("Chặn người dùng thất bại");
    }
  };

  const handleRemoveComment = (comment: Comment) => {
    // đóng menu
    setPostMenuOpen((prev) => ({ ...prev, [comment.commentId]: false }));

    // dùng requestAnimationFrame để chắc chắn render cập nhật
    requestAnimationFrame(() => {
      setSelectedComment(comment); // lưu bài viết đang gỡ
      setIsApproveOpen(true); // mở modal
    });
  };

  const handleRemoveCommentLocal = (commentId: string) => {
    // 1. update posts
    setPosts((prevPosts) =>
      prevPosts.map((post) => {
        if (post._id !== activePost._id) return post;
        return {
          ...post,
          comments: post.comments?.filter((cmt) => cmt.commentId !== commentId),
        };
      }),
    );

    // 2. update activePost (RẤT QUAN TRỌNG)
    if (activePost) {
      const updatedComments = activePost.comments?.filter(
        (cmt) => cmt.commentId !== commentId,
      );

      Object.assign(activePost, { comments: updatedComments });
      onCommentAdded(""); // ép re-render modal
    }
  };

  const handleRemovePostLocal = (postId: string) => {
    // 1. Cập nhật danh sách post trong PostDetail
    setPosts((prev) => prev.filter((p) => p._id !== postId));

    // 2. Đóng modal chi tiết
    onClose();

    // 3. Reset state liên quan
    setIsApproveOpen(false);
    setSelectedPost(null);

    // 4. Thông báo cho parent (nếu có callback)
    if (onPostDeleted) onPostDeleted(postId);
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

          // đóng modal
          onClose();

          // thông báo cho cha cập nhật danh sách
          if (onPostDeleted) onPostDeleted(postId);
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

  const handleRemove = (post: Post) => {
    setPostMenuOpen((prev) => ({ ...prev, [post._id]: false }));

    // dùng requestAnimationFrame để chắc chắn render cập nhật
    requestAnimationFrame(() => {
      setSelectedPost(post); // lưu bài viết đang gỡ
      setIsApproveOpen(true); // mở modal
    });
  };
  const handleReply = (comment: any) => {
    if (!activePost?._id) return;

    const username =
      userInfoMap[comment.commentBy]?.fullName || comment.commentBy;

    // Nếu đang trả lời chính mình => không tag
    const tag = comment.commentBy !== currentUserEmail ? `@${username}# ` : "";

    // 👉 lưu comment đang reply
    setReplyingTo(comment);

    // 👉 set text input
    setCommentText((prev) => ({
      ...prev,
      [activePost._id]: tag,
    }));

    // 👉 focus input
    setTimeout(() => {
      commentInputRef.current?.focus();
    }, 0);
  };

  const resetTextareaHeight = () => {
    if (commentInputRef.current) {
      commentInputRef.current.style.height = "auto";
    }
  };

  const handleSelectUser = (user: any) => {
    if (!activePost?._id || !mentionRange) return;

    const currentText = commentText[activePost._id] || "";

    const newText =
      currentText.slice(0, mentionRange.start) +
      `@${user.name}# ` +
      currentText.slice(mentionRange.end);

    setCommentText((prev) => ({
      ...prev,
      [activePost._id]: newText,
    }));

    setShowDropdown(false);

    // 🔥 FIX: focus lại textarea + set cursor
    setTimeout(() => {
      if (commentInputRef.current) {
        const pos = mentionRange.start + user.name.length + 2; // "@name "
        commentInputRef.current.focus();
        commentInputRef.current.setSelectionRange(pos, pos);
      }
    }, 0);
  };

  const focusCommentInput = () => {
    requestAnimationFrame(() => {
      commentInputRef.current?.focus();
    });
  };
  const handleSelectFiles = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);

    setCommentFiles((prev) => [...prev, ...files]);

    const newPreviews: PreviewFile[] = files.map((file) => {
      const url = URL.createObjectURL(file);

      if (file.type.startsWith("video")) {
        return {
          url,
          type: "video",
          name: file.name,
        };
      }

      if (file.type.startsWith("image")) {
        return {
          url,
          type: "image",
          name: file.name,
        };
      }

      return {
        url,
        type: "file",
        name: file.name,
      };
    });

    setPreviewUrls((prev) => [...prev, ...newPreviews]);

    focusCommentInput();
  };

  const uploadFiles = async (files: File[]) => {
    const uploadPromises = files.map(async (file) => {
      const uploadRes = await FileService.uploadPicture(file);
      return uploadRes.url; // 🔥 dùng luôn URL từ backend
    });

    return Promise.all(uploadPromises);
  };
  const handleRemoveFile = (index: number) => {
    setCommentFiles((prev) => prev.filter((_, i) => i !== index));

    setPreviewUrls((prev) => {
      const file = prev[index];
      URL.revokeObjectURL(file.url); // tránh leak memory
      return prev.filter((_, i) => i !== index);
    });
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

  const isVideo = (url: string) => {
    return (
      url.includes(".mp4") ||
      url.includes(".webm") ||
      url.includes(".mov") ||
      url.includes("video")
    );
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

  return (
    <div className="post-detail-overlay" onClick={onClose}>
      <AnimatePresence>
        <motion.div
          className="commentOverlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="commentModal"
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0.95 }}
            transition={{ duration: 0.2 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="commentModalLeft">
              {/* CASE 1: Bài viết chia sẻ */}
              {activePost.postType === "share" ? (
                <div className="shared-post-placeholder">
                  <button
                    className="go-to-shared-post"
                    onClick={(e) => {
                      e.stopPropagation();

                      if (!activePost.postId) return;

                      // 🔥 GỌI LÊN CHA
                      onOpenOriginalPost(activePost.postId);
                    }}
                  >
                    🔗 Đi đến bài viết được chia sẻ
                  </button>
                </div>
              ) : activePost.thumbnails_url &&
                activePost.thumbnails_url.length > 0 ? (
                /* CASE 2: Bài thường có ảnh/video */
                <div className="postImg">
                  <div
                    className="postSlider"
                    style={{
                      transform: `translateX(-${
                        getIndex(activePost._id) * 100
                      }%)`,
                    }}
                  >
                    {activePost.thumbnails_url.map((url, idx) => {
                      const fileName = activePost.thumbnails?.[idx] || "";

                      return (
                        <div className="slide" key={idx}>
                          {/\.mp4|\.mov$/i.test(fileName) ? (
                            <video className="model-postVideo" controls>
                              <source src={url} type="video/mp4" />
                            </video>
                          ) : (
                            <img
                              className="model-postImage"
                              src={url}
                              alt={activePost.title}
                            />
                          )}
                        </div>
                      );
                    })}
                  </div>

                  {/* Navigation */}
                  {activePost.thumbnails_url.length > 1 && (
                    <>
                      {getIndex(activePost._id) > 0 && (
                        <ChevronLeftOutlinedIcon
                          className="nav-left"
                          onClick={() =>
                            handlePrev(
                              activePost._id,
                              activePost.thumbnails_url.length,
                            )
                          }
                        />
                      )}

                      {getIndex(activePost._id) <
                        activePost.thumbnails_url.length - 1 && (
                        <ChevronRightOutlinedIcon
                          className="nav-right"
                          onClick={() =>
                            handleNext(
                              activePost._id,
                              activePost.thumbnails_url.length,
                            )
                          }
                        />
                      )}
                    </>
                  )}

                  {/* Dots */}
                  {activePost.thumbnails_url.length > 1 && (
                    <div className="dots-post">
                      {activePost.thumbnails_url.map((_, idx) => (
                        <span
                          key={idx}
                          className={`dot-post ${
                            idx === getIndex(activePost._id) ? "active" : ""
                          }`}
                          onClick={() =>
                            setSlideIndex((prev) => ({
                              ...prev,
                              [activePost._id]: idx,
                            }))
                          }
                        />
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                /* CASE 3: Bài thường không có ảnh */
                <p>Không có ảnh</p>
              )}
            </div>

            <div className="commentModalRight">
              <div className="modalHeader">
                <div className="cm-postInfo" style={{ cursor: "pointer" }}>
                  <img
                    className="postInfoImg"
                    src={userInfoMap[activePost.createdBy]?.avatar || ""}
                    alt="avatar"
                    onClick={() => goToProfile(activePost.createdBy)}
                  />
                  <div className="postInfoText">
                    <div
                      className="postInfoName"
                      onClick={() => goToProfile(activePost.createdBy)}
                    >
                      {userInfoMap[activePost.createdBy]?.fullName ||
                        activePost.createdBy}
                    </div>
                  </div>

                  {currentUserRole !== "Administrator" && (
                    <button
                      className="closeModal"
                      onClick={(e) => {
                        e.stopPropagation();
                        togglePostMenu(activePost._id);
                      }}
                    >
                      <MoreHorizOutlinedIcon />
                    </button>
                  )}

                  <div
                    className="postMenu"
                    ref={(el) => {
                      menuRefs.current[activePost._id] = el;
                    }}
                  >
                    {postMenuOpen[activePost._id] && (
                      <div className="menuDropdown">
                        {activePost.createdBy === currentUserEmail ? (
                          <>
                            <div
                              className="menuItem"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleEditPost(activePost);
                              }}
                            >
                              ✏️ Chỉnh sửa bài đăng
                            </div>

                            <div
                              className="menuItem delete"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeletePost(activePost._id);
                              }}
                            >
                              🗑️ Xóa bài đăng
                            </div>
                          </>
                        ) : (
                          <>
                            {currentUserRole !== "Moderator" && (
                              <div
                                className="menuItem"
                                onClick={() => handleReport(activePost)}
                              >
                                🚩 Báo cáo bài đăng
                              </div>
                            )}

                            {currentUserRole === "Moderator" && (
                              <div
                                className="menuItem delete"
                                onClick={() => handleRemove(activePost)}
                              >
                                🛑 Gỡ bài viết
                              </div>
                            )}

                            <div
                              className="menuItem block"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleBlock(activePost.createdBy);
                                setPostMenuOpen((prev) => ({
                                  ...prev,
                                  [activePost._id]: false,
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
              </div>
              <div className="postTitle">
                <span>{activePost.title}</span>
              </div>

              <div className="postContent">
                <p>
                  {expandedPosts[activePost._id]
                    ? activePost.content
                    : truncateWords(activePost.content, 100)}
                </p>
                {activePost.content.split(" ").length > 100 && (
                  <button
                    className="toggleReadMore"
                    onClick={() =>
                      setExpandedPosts((prev) => ({
                        ...prev,
                        [activePost._id]: !prev[activePost._id],
                      }))
                    }
                  >
                    {expandedPosts[activePost._id] ? "Thu gọn" : "Xem thêm"}
                  </button>
                )}
              </div>
              <div className="iconBlock">
                <div className="leftIcon">
                  <div
                    className="like-container"
                    onMouseEnter={(e) => {
                      e.stopPropagation();
                      setPostPopoverMap((prev) => ({
                        ...prev,
                        [activePost._id]: true,
                      }));
                    }}
                    onMouseLeave={(e) => {
                      e.stopPropagation();
                      setPostPopoverMap((prev) => ({
                        ...prev,
                        [activePost._id]: false,
                      }));
                    }}
                  >
                    <button
                      className={`react-btn ${
                        userReactMap[activePost._id]
                          ? `active-${userReactMap[activePost._id]}`
                          : ""
                      }`}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleReact(activePost._id, "love");
                      }}
                    >
                      {userReactMap[activePost._id] === "love" ? (
                        "❤️"
                      ) : userReactMap[activePost._id] === "like" ? (
                        "👍"
                      ) : userReactMap[activePost._id] === "haha" ? (
                        "😂"
                      ) : userReactMap[activePost._id] === "wow" ? (
                        "😮"
                      ) : userReactMap[activePost._id] === "sad" ? (
                        "😢"
                      ) : userReactMap[activePost._id] === "angry" ? (
                        "😡"
                      ) : (
                        <FavoriteBorderOutlinedIcon />
                      )}
                    </button>

                    {postPopoverMap[activePost._id] && (
                      <div
                        className="emote-popover"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <span
                          onClick={() => handleReact(activePost._id, "love")}
                        >
                          ❤️
                        </span>
                        <span
                          onClick={() => handleReact(activePost._id, "like")}
                        >
                          👍
                        </span>
                        <span
                          onClick={() => handleReact(activePost._id, "haha")}
                        >
                          😂
                        </span>
                        <span
                          onClick={() => handleReact(activePost._id, "wow")}
                        >
                          😮
                        </span>
                        <span
                          onClick={() => handleReact(activePost._id, "sad")}
                        >
                          😢
                        </span>
                        <span
                          onClick={() => handleReact(activePost._id, "angry")}
                        >
                          😡
                        </span>
                      </div>
                    )}
                  </div>

                  {activePost.createdBy !== currentUserEmail && (
                    <ShareOutlinedIcon
                      sx={{
                        fontSize: "23px",
                        marginLeft: "8px",
                        cursor: "pointer",
                      }}
                      onClick={(e) => {
                        e.stopPropagation(); // Ngăn overlay của PostDetail đóng
                        setSharePost(activePost);
                        setOpenShareModal(true);
                      }}
                    />
                  )}
                </div>
              </div>

              <div className="modalComments">
                <div className="comment-list" ref={commentListRef}>
                  {activePost.comments && activePost.comments.length > 0 ? (
                    activePost.comments
                      ?.filter((comment) => comment.statusComment !== "hidden")
                      .map((comment) => (
                        <div
                          key={comment.commentId}
                          id={`comment-${comment.commentId}`} // 👈 thêm
                          className="comment-card"
                        >
                          <img
                            src={userInfoMap[comment.commentBy]?.avatar || ""}
                            alt="Avatar"
                            className="comment-avatar"
                            style={{ cursor: "pointer" }}
                            onClick={() => goToProfile(comment.commentBy)}
                          />
                          <div className="comment-body">
                            <div
                              className="comment-header"
                              onClick={() => goToProfile(comment.commentBy)}
                              style={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                                cursor: "pointer",
                              }}
                            >
                              <div>
                                <span className="comment-username">
                                  {userInfoMap[comment.commentBy]?.fullName ||
                                    comment.commentBy}
                                </span>
                                <span className="comment-time">
                                  {comment.createdAt
                                    ? formatTimeVN(comment.createdAt)
                                    : ""}
                                </span>
                              </div>

                              {/* 3 chấm menu */}
                              {currentUserRole !== "Administrator" && (
                                <div
                                  className="comment-options"
                                  style={{ position: "relative" }}
                                >
                                  <button
                                    className="options-btn"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setOpenCommentMenu((prev) => ({
                                        ...prev,
                                        [comment.commentId]:
                                          !prev[comment.commentId],
                                      }));
                                    }}
                                  >
                                    ⋮
                                  </button>

                                  {openCommentMenu[comment.commentId] && (
                                    <div
                                      className="comment-menu"
                                      style={{
                                        position: "absolute",
                                        top: "20px",
                                        right: 0,
                                        background: "#fff",
                                        border: "1px solid #ccc",
                                        borderRadius: "6px",
                                        zIndex: 10,
                                        boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
                                        marginTop: "15px",
                                      }}
                                    >
                                      {/* 👉 CHỦ BÌNH LUẬN */}
                                      {comment.commentBy ===
                                      currentUserEmail ? (
                                        <button
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            handleDeleteComment(
                                              activePost._id,
                                              comment.commentId,
                                            );
                                            setOpenCommentMenu({});
                                          }}
                                          style={{
                                            padding: "6px 12px",
                                            background: "none",
                                            border: "none",
                                            cursor: "pointer",
                                            width: "170px",
                                            textAlign: "left",
                                            color: "#e53935",
                                          }}
                                        >
                                          ❌ Xóa bình luận
                                        </button>
                                      ) : currentUserRole === "Moderator" ? (
                                        /* 👉 KHÔNG PHẢI CHỦ & LÀ MOD */
                                        <button
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            handleRemoveComment(comment);
                                            setOpenCommentMenu({});
                                          }}
                                          style={{
                                            padding: "6px 12px",
                                            background: "none",
                                            border: "none",
                                            cursor: "pointer",
                                            width: "170px",
                                            textAlign: "left",
                                            color: "#d32f2f",
                                          }}
                                        >
                                          🛑 Gỡ bình luận
                                        </button>
                                      ) : (
                                        /* 👉 USER THƯỜNG */
                                        <button
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            setReportComment(comment);
                                            setReportModalOpen(true);
                                            setOpenCommentMenu({});
                                          }}
                                          style={{
                                            padding: "6px 12px",
                                            background: "none",
                                            border: "none",
                                            cursor: "pointer",
                                            width: "170px",
                                            textAlign: "left",
                                          }}
                                        >
                                          🚩 Báo cáo bình luận
                                        </button>
                                      )}
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>

                            <div className="comment-content">
                              {renderContentWithTags(comment.content)}
                            </div>
                            {comment.thumbnails &&
                              comment.thumbnails.length > 0 && (
                                <div className="comment-thumbnail">
                                  {comment.thumbnails[0] &&
                                  isVideo(comment.thumbnails[0]) ? (
                                    <video
                                      src={comment.thumbnails[0]}
                                      className="comment-thumbnail-img"
                                      controls
                                    />
                                  ) : (
                                    <img
                                      src={comment.thumbnails[0]}
                                      alt="comment-thumbnail"
                                      className="comment-thumbnail-img"
                                    />
                                  )}
                                </div>
                              )}
                            <div className="comment-reacts">
                              <div
                                className="like-container"
                                onMouseEnter={() =>
                                  setCommentPopoverMap((prev) => ({
                                    ...prev,
                                    [comment.commentId]: true,
                                  }))
                                }
                                onMouseLeave={() =>
                                  setCommentPopoverMap((prev) => ({
                                    ...prev,
                                    [comment.commentId]: false,
                                  }))
                                }
                              >
                                <button
                                  className={`react-btn ${
                                    userCommentReactMap[comment.commentId]
                                      ? `active-${
                                          userCommentReactMap[comment.commentId]
                                        }`
                                      : ""
                                  }`}
                                  onClick={() =>
                                    handleCommentReact(
                                      activePost._id || "",
                                      comment.commentId,
                                      "love",
                                    )
                                  }
                                >
                                  {userCommentReactMap[comment.commentId] ===
                                  "love" ? (
                                    "❤️"
                                  ) : userCommentReactMap[comment.commentId] ===
                                    "like" ? (
                                    "👍"
                                  ) : userCommentReactMap[comment.commentId] ===
                                    "haha" ? (
                                    "😂"
                                  ) : userCommentReactMap[comment.commentId] ===
                                    "wow" ? (
                                    "😮"
                                  ) : userCommentReactMap[comment.commentId] ===
                                    "sad" ? (
                                    "😢"
                                  ) : userCommentReactMap[comment.commentId] ===
                                    "angry" ? (
                                    "😡"
                                  ) : (
                                    <FavoriteBorderOutlinedIcon />
                                  )}
                                </button>

                                {commentPopoverMap[comment.commentId] && (
                                  <div
                                    className="emote-popover"
                                    onClick={(e) => e.stopPropagation()}
                                  >
                                    <span
                                      onClick={() =>
                                        handleCommentReact(
                                          activePost._id || "",
                                          comment.commentId,
                                          "love",
                                        )
                                      }
                                    >
                                      ❤️
                                    </span>
                                    <span
                                      onClick={() =>
                                        handleCommentReact(
                                          activePost._id || "",
                                          comment.commentId,
                                          "like",
                                        )
                                      }
                                    >
                                      👍
                                    </span>
                                    <span
                                      onClick={() =>
                                        handleCommentReact(
                                          activePost._id || "",
                                          comment.commentId,
                                          "haha",
                                        )
                                      }
                                    >
                                      😂
                                    </span>
                                    <span
                                      onClick={() =>
                                        handleCommentReact(
                                          activePost._id || "",
                                          comment.commentId,
                                          "wow",
                                        )
                                      }
                                    >
                                      😮
                                    </span>
                                    <span
                                      onClick={() =>
                                        handleCommentReact(
                                          activePost._id || "",
                                          comment.commentId,
                                          "sad",
                                        )
                                      }
                                    >
                                      😢
                                    </span>
                                    <span
                                      onClick={() =>
                                        handleCommentReact(
                                          activePost._id || "",
                                          comment.commentId,
                                          "angry",
                                        )
                                      }
                                    >
                                      😡
                                    </span>
                                  </div>
                                )}
                              </div>
                              {Object.values(comment.reacts || {}).reduce(
                                (s, arr) => s + arr.length,
                                0,
                              ) > 0 && (
                                <label
                                  className="countReact-Comment"
                                  onClick={() => {
                                    setSelectedReactComment(comment); // nếu muốn mở modal react cho comment
                                    setReactModalOpen(true);
                                  }}
                                >
                                  {Object.values(comment.reacts || {}).reduce(
                                    (s, arr) => s + arr.length,
                                    0,
                                  )}{" "}
                                  lượt bày tỏ cảm xúc
                                </label>
                              )}
                              <button
                                className="reply-btn"
                                onClick={() => handleReply(comment)}
                              >
                                Trả lời
                              </button>
                            </div>
                            {replyCountMap[comment.commentId] > 0 && (
                              <div className="countReply">
                                <button
                                  className="view-replies-btn"
                                  onClick={() =>
                                    setOpenReplyMap((prev) => ({
                                      ...prev,
                                      [comment.commentId]:
                                        !prev[comment.commentId],
                                    }))
                                  }
                                >
                                  Xem {replyCountMap[comment.commentId]} phản
                                  hồi
                                </button>

                                {/* Nếu đang mở, hiển thị ReplyComment */}
                                {openReplyMap[comment.commentId] && (
                                  <ReplyComment
                                    postId={activePost._id}
                                    parentId={comment.commentId}
                                    userInfoMap={userInfoMap}
                                    newReply={newReply[comment.commentId]}
                                    onReply={(reply) => {
                                      const username =
                                        userInfoMap[reply.commentBy]
                                          ?.fullName || reply.commentBy;

                                      // 🔹 Nếu reply của chính mình thì không tag
                                      const tag =
                                        reply.commentBy !== currentUserEmail
                                          ? `@${username}# `
                                          : "";

                                      setReplyingTo(reply);

                                      setCommentText((prev) => ({
                                        ...prev,
                                        [activePost._id]: tag,
                                      }));

                                      setTimeout(
                                        () => commentInputRef.current?.focus(),
                                        0,
                                      );
                                    }}
                                  />
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      ))
                  ) : (
                    <p className="no-comment">Chưa có bình luận nào</p>
                  )}
                </div>
              </div>
              {replyingTo && (
                <div className="replying-box">
                  Đang trả lời
                  {replyingTo.commentBy !== currentUserEmail && (
                    <>
                      {" "}
                      <b>
                        {userInfoMap[replyingTo.commentBy]?.fullName ||
                          replyingTo.commentBy}
                      </b>
                    </>
                  )}
                  <span
                    style={{ marginLeft: 10, cursor: "pointer" }}
                    onClick={() => setReplyingTo(null)}
                  >
                    ✕
                  </span>
                </div>
              )}
              <div
                className="commentInput"
                onClick={(e) => e.stopPropagation()}
              >
                {/* EMOJI */}
                <div className="emojiWrapper">
                  <InsertEmoticonOutlinedIcon
                    sx={{ fontSize: 22, color: "#777", cursor: "pointer" }}
                    onClick={(e) => {
                      e.stopPropagation();
                      setOpenEmojiPicker((prev) =>
                        prev?.type === "modal"
                          ? null
                          : { type: "modal", postId: activePost._id || "" },
                      );
                    }}
                  />

                  {openEmojiPicker?.type === "modal" &&
                    openEmojiPicker.postId === (activePost._id || "") && (
                      <div className="emojiPickerContainer">
                        <EmojiPicker
                          onEmojiClick={(emojiData) =>
                            handleEmojiClick(activePost._id || "", emojiData)
                          }
                        />
                      </div>
                    )}
                </div>

                {/* UPLOAD MEDIA */}
                <div className="uploadWrapper">
                  <label htmlFor="commentUpload">
                    <AddToPhotosIcon />
                  </label>

                  <input
                    id="commentUpload"
                    type="file"
                    accept="image/*,video/*"
                    multiple
                    style={{ display: "none" }}
                    onChange={handleSelectFiles}
                  />
                </div>

                {/* TEXTAREA + HIGHLIGHT */}
                <div className="textAreaWrapper">
                  {/* Layer hiển thị highlight */}
                  <div className="highlight-layer">
                    {renderContentWithTags(
                      activePost?._id ? commentText[activePost._id] || "" : "",
                    )}
                  </div>

                  {/* Textarea thật */}
                  <textarea
                    ref={commentInputRef}
                    value={
                      activePost?._id ? commentText[activePost._id] || "" : ""
                    }
                    onChange={(e) => {
                      if (!activePost?._id) return;

                      const value = e.target.value;

                      setCommentText((prev) => ({
                        ...prev,
                        [activePost._id]: value,
                      }));

                      // Auto resize
                      e.target.style.height = "auto";
                      e.target.style.height = `${e.target.scrollHeight}px`;

                      // 🔥 HANDLE MENTION
                      const cursor = e.target.selectionStart;
                      const textBeforeCursor = value.slice(0, cursor);

                      const match = textBeforeCursor.match(/@([^\s@]*)$/);

                      if (match) {
                        const keyword = match[1].toLowerCase();

                        const filtered = userList.filter((user) =>
                          user.name.toLowerCase().includes(keyword),
                        );

                        setSuggestions(filtered);
                        setShowDropdown(true);

                        setMentionRange({
                          start: cursor - match[0].length,
                          end: cursor,
                        });
                      } else {
                        setShowDropdown(false);
                        setMentionRange(null);
                      }
                    }}
                    onScroll={(e) => {
                      const target = e.target as HTMLTextAreaElement;
                      const highlight =
                        target.previousSibling as HTMLDivElement;
                      if (highlight) {
                        highlight.scrollTop = target.scrollTop;
                      }
                    }}
                    placeholder="Bình luận..."
                    className="commentBox"
                    rows={1}
                    onKeyDown={(e) => {
                      if (!activePost?._id) return;

                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleAddComment(activePost._id);
                      }
                    }}
                  />
                  {showDropdown && suggestions.length > 0 && (
                    <div className="mention-dropdown">
                      {suggestions.map((user) => (
                        <div
                          key={user.id}
                          className="mention-item"
                          onClick={() => handleSelectUser(user)}
                        >
                          <img
                            src={user.avatar}
                            alt=""
                            className="mention-avatar"
                          />
                          <span>{user.name}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              {previewUrls.length > 0 && (
                <div className="previewCmt-container">
                  {previewUrls.map((item, index) => (
                    <div key={index} className="previewCmt-item">
                      {/* IMAGE */}
                      {item.type === "image" ? (
                        <img src={item.url} className="previewCmt-img" />
                      ) : null}

                      {/* VIDEO */}
                      {item.type === "video" ? (
                        <video
                          src={item.url}
                          className="previewCmt-img"
                          controls
                        />
                      ) : null}

                      {/* FILE (pdf, docx, zip...) */}
                      {item.type === "file" ? (
                        <div className="file-cmt-preview">
                          📄 <span className="file-cmt-name">{item.name}</span>
                        </div>
                      ) : null}

                      {/* REMOVE BUTTON */}
                      <button
                        className="remove-preview-btn"
                        onClick={() => handleRemoveFile(index)}
                      >
                        x
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      </AnimatePresence>
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
      {selectedComment && (
        <ApproveModal
          isOpen={isApproveOpen}
          onClose={() => setIsApproveOpen(false)}
          policy_element="bình luận"
          element="comment"
          elementId={selectedComment.commentId}
          elementParentId={activePost._id}
          currentUserEmail={currentUserEmail ?? ""}
          comment={selectedComment}
          onRemoved={() => handleRemoveCommentLocal(selectedComment.commentId)}
        />
      )}
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

      {reportComment && reportModalOpen && (
        <ReportModal
          isOpen={reportModalOpen}
          onClose={() => {
            setReportModalOpen(false);
            setReportComment(null);
          }}
          policy_type="bình luận"
          type="comment"
          content={reportComment.content}
          contentId={reportComment.commentId}
          contentParentId={activePost._id}
          violatorEmail={reportComment.commentBy}
        />
      )}
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

      <EditPost
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingPost(null);
        }}
        post={editingPost}
        onPostUpdated={async () => {
          if (!editingPost) return;

          try {
            const res = await postAPI.getById(editingPost._id);
            if (onActivePostUpdate) {
              onActivePostUpdate(res.post || res);
            }
          } catch (err) {
            console.error("Không thể load lại post sau khi edit:", err);
          }

          setIsModalOpen(false);
          setEditingPost(null);
        }}
      />
    </div>
  );
};

export default PostDetail;
