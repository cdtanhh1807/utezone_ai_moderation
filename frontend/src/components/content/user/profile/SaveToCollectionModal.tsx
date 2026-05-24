import { useEffect, useState } from "react";
import "./SaveToCollectionModal.css";
import { savedAPI } from "../../../../services/SavedService";
import { postAPI } from "../../../../services/PostService";
import { ToastService } from "../../../../services/ToastService";

interface Props {
  postId: string;
  email: string;
  onClose: () => void;
}

interface RawCollection {
  name: string;
  posts: string[];
}

interface PostPreview {
  _id: string;
  image: string;
  createdAt: string;
}

interface CollectionUI {
  id: number;
  name: string;
  posts: PostPreview[];
  isDisabled?: boolean;
}

function SaveToCollectionModal({ postId, email, onClose }: Props) {
  const [collections, setCollections] = useState<CollectionUI[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (!email) return;
    fetchCollections();
  }, [email]);

  const fetchCollections = async () => {
    try {
      setLoading(true);

      const res = await savedAPI.getCollections(email);
      const raw: RawCollection[] = res?.post_saved?.collections || [];

      const mapped: CollectionUI[] = await Promise.all(
        raw.map(async (col, index) => {
          const posts: PostPreview[] = await Promise.all(
            (col.posts || []).slice(0, 3).map(async (pId: string) => {
              try {
                const resPost = await postAPI.getById(pId);
                const post = resPost?.post;

                return {
                  _id: pId,
                  image:
                    post?.thumbnails_url?.[0] ||
                    post?.image ||
                    "https://via.placeholder.com/150",
                  createdAt:
                    post?.createdAt || new Date().toISOString(),
                };
              } catch {
                return {
                  _id: pId,
                  image: "https://via.placeholder.com/150",
                  createdAt: new Date().toISOString(),
                };
              }
            })
          );

          // ✅ CHECK POST ĐÃ TỒN TẠI CHƯA
          const isDisabled = (col.posts || []).includes(postId);

          return {
            id: index,
            name: col.name,
            posts,
            isDisabled,
          };
        })
      );

      setCollections(mapped);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveToCollection = async (collectionName: string) => {
    try {
      await savedAPI.addPostToCollection({
        collection_name: collectionName,
        post_id: postId,
      });
      ToastService.success(`Đã lưu vào bộ sưu tập "${collectionName}"`);

      onClose();
    } catch (err) {
      console.error(err);
      ToastService.error("Có lỗi xảy ra khi lưu bài viết");
    }
  };

  const handleCreateCollection = async () => {
    if (!newName.trim()) return;

    try {
      setCreating(true);

      await savedAPI.addCollection({
        collection_name: newName,
      });

      await savedAPI.addPostToCollection({
        collection_name: newName,
        post_id: postId,
      });

      setShowCreate(false);
      setNewName("");

      onClose();
    } catch (err) {
      console.error(err);
      setCreating(false);
    }
  };

  return (
    <div className="save-modal-overlay" onClick={onClose}>
      <div
        className="save-modal-container"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="save-modal-title">Lưu bài viết</h3>

        {loading ? (
          <div>Đang tải...</div>
        ) : (
          <>
            {/* COLLECTION LIST */}
            {collections.map((col) => (
              <div
                key={col.id}
                className={`save-modal-collection ${
                  col.isDisabled ? "disabled" : ""
                }`}
                onClick={() => {
                  if (col.isDisabled) return;
                  handleSaveToCollection(col.name);
                }}
              >
                <h3 className="save-modal-collection-title">
                  {col.name}
                </h3>

                <div className="save-modal-grid">
                  {col.posts.map((post) => (
                    <div key={post._id} className="save-modal-item">
                      <img src={post.image} alt="saved" />

                      <div className="save-modal-overlay-text">
                        {new Date(post.createdAt).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {/* CREATE BUTTON */}
            {!creating && !showCreate && (
              <div
                className="save-modal-create"
                onClick={() => setShowCreate(true)}
              >
                ➕ Tạo bộ sưu tập mới
              </div>
            )}

            {/* CREATE INPUT */}
            {showCreate && (
              <div className="save-modal-create-box">
                <input
                  placeholder="Tên bộ sưu tập..."
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                />

                <button onClick={handleCreateCollection}>
                  Tạo bộ sưu tập mới & Lưu bài viết
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default SaveToCollectionModal;