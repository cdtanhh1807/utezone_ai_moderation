import { useEffect, useRef, useState } from "react";
import "./profileSaved.css";
import { savedAPI } from "../../../../services/SavedService";
import { postAPI } from "../../../../services/PostService";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import ModeEditOutlinedIcon from "@mui/icons-material/ModeEditOutlined";
import MoreHorizOutlinedIcon from "@mui/icons-material/MoreHorizOutlined";
import PostDetail from "../post/postDetail";

interface Post {
  _id: string;
  image: string;
  createdAt: string;
}

interface Collection {
  id: string;
  name: string;
  posts: Post[];
}

function ProfileSaved({ email }: { email?: string }) {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loading, setLoading] = useState(true);
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [openPostMenu, setOpenPostMenu] = useState<string | null>(null);
  const [activePost, setActivePost] = useState<any>(null);
  const [isPostDetailOpen, setIsPostDetailOpen] = useState(false);
  const [renameModal, setRenameModal] = useState<{
    open: boolean;
    oldName: string;
    newName: string;
  }>({
    open: false,
    oldName: "",
    newName: "",
  });

  useEffect(() => {
    if (!email) return;

    const fetchCollections = async () => {
      try {
        setLoading(true);
        const res = await savedAPI.getCollections(email);

        const rawCollections = res?.post_saved?.collections || [];

        const mappedCollections: Collection[] = await Promise.all(
          rawCollections.map(async (col: any, index: number) => {
            const posts: Post[] = await Promise.all(
              (col.posts || []).map(async (postId: string) => {
                try {
                  const resPost = await postAPI.getById(postId);
                  const post = resPost?.post;

                  return {
                    _id: postId,
                    image:
                      post?.thumbnails_url?.[0] ||
                      post?.image ||
                      "https://via.placeholder.com/300",
                    createdAt: post?.createdAt || new Date().toISOString(),
                  };
                } catch {
                  return {
                    _id: postId,
                    image: "https://via.placeholder.com/300",
                    createdAt: new Date().toISOString(),
                  };
                }
              }),
            );

            return {
              id: `${index}`,
              name: col.name,
              posts,
            };
          }),
        );

        setCollections(mappedCollections);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchCollections();
  }, [email]);

  const menuRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpenMenu(null);
        setOpenPostMenu(null);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // 🗑 XÓA POST KHỎI COLLECTION
  const handleRemovePost = async (collectionName: string, postId: string) => {
    try {
      await savedAPI.removePostFromCollection({
        collection_name: collectionName,
        post_id: postId,
      });

      setCollections((prev) =>
        prev.map((col) =>
          col.name === collectionName
            ? {
                ...col,
                posts: col.posts.filter((p) => p._id !== postId),
              }
            : col,
        ),
      );
    } catch (err) {
      console.error(err);
    }
  };

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

  // 🗑 XÓA COLLECTION
  const handleDeleteCollection = async (collectionName: string) => {
    try {
      await savedAPI.deleteCollection({
        collection_name: collectionName,
      });

      setCollections((prev) => prev.filter((c) => c.name !== collectionName));
    } catch (err) {
      console.error(err);
    }
  };

  // ✏️ RENAME COLLECTION
  const handleRenameCollection = async () => {
    const { oldName, newName } = renameModal;

    if (!newName.trim()) return;

    try {
      await savedAPI.addCollection({
        collection_name: newName,
      });

      const col = collections.find((c) => c.name === oldName);

      if (col) {
        for (const post of col.posts) {
          await savedAPI.addPostToCollection({
            collection_name: newName,
            post_id: post._id,
          });
        }

        await savedAPI.deleteCollection({
          collection_name: oldName,
        });
      }

      setCollections((prev) =>
        prev.map((c) => (c.name === oldName ? { ...c, name: newName } : c)),
      );

      // đóng modal
      setRenameModal({ open: false, oldName: "", newName: "" });
    } catch (err) {
      console.error(err);
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

  if (loading) return <div>Đang tải bộ sưu tập...</div>;
  if (collections.length === 0) return <div>Bạn chưa có bộ sưu tập nào 📌</div>;

  return (
    <div className="saved-container">
      {collections.map((col) => (
        <div key={col.id} className="collection">
          {/* COLLECTION HEADER */}
          <div className="collection-title-row">
            <h3 className="collection-title">{col.name}</h3>

            <div
              className="dots"
              onClick={() =>
                setOpenMenu(openMenu === col.name ? null : col.name)
              }
            >
              <MoreHorizOutlinedIcon />
              {openMenu === col.name && (
                <div className="menu" ref={menuRef}>
                  <div
                    onClick={() =>
                      setRenameModal({
                        open: true,
                        oldName: col.name,
                        newName: col.name,
                      })
                    }
                  >
                    <ModeEditOutlinedIcon /> Đổi tên bộ sưu tập
                  </div>

                  <div onClick={() => handleDeleteCollection(col.name)}>
                    <DeleteOutlinedIcon /> Xóa bộ sưu tập
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* POSTS */}
          <div className="collection-grid">
            {col.posts.map((post) => (
              <div
                key={post._id}
                className="collection-item"
                onClick={() => handleOpenPost(post._id)}
              >
                <div
                  className="post-dots"
                  onClick={() =>
                    setOpenPostMenu(openPostMenu === post._id ? null : post._id)
                  }
                >
                  <DeleteOutlinedIcon
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemovePost(col.name, post._id);
                    }}
                  />
                </div>

                <img src={post.image} alt="saved" />

                <div className="overlay">
                  {new Date(post.createdAt).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {isPostDetailOpen && activePost && (
        <PostDetail
          activePost={activePost}
          onClose={() => setIsPostDetailOpen(false)}
          onCommentAdded={refreshPost}
          onOpenOriginalPost={openOriginalPost}
        />
      )}
      {renameModal.open && (
        <div className="rename-modal-overlay">
          <div className="rename-modal">
            <h3>Đổi tên bộ sưu tập</h3>

            <input
              value={renameModal.newName}
              onChange={(e) =>
                setRenameModal((prev) => ({
                  ...prev,
                  newName: e.target.value,
                }))
              }
              className="rename-input"
              autoFocus
            />

            <div className="rename-actions">
              <button
                onClick={() =>
                  setRenameModal({ open: false, oldName: "", newName: "" })
                }
              >
                Hủy
              </button>

              <button onClick={handleRenameCollection}>Lưu</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ProfileSaved;
