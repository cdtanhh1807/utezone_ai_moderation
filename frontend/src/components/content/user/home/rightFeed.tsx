import { useEffect, useState } from "react";
import { postAPI } from "../../../../services/PostService";
import AccountService from "../../../../services/AccountService";
import type { Post } from "../../../../types/Post";
import { useNavigate } from "react-router-dom";

interface AccountInfo {
  fullName: string;
  avatar: string;
}

interface RightFeedProps {
  onOpenPostDetail: (post: Post) => void;
}

export default function RightFeed({ onOpenPostDetail }: RightFeedProps) {
  const [suggestedPosts, setSuggestedPosts] = useState<Post[]>([]);
  const [accountMap, setAccountMap] = useState<Record<string, AccountInfo>>({});
  const navigate = useNavigate();

  // ================= FETCH POSTS =================
  useEffect(() => {
    const fetchSuggestedPosts = async () => {
      try {
        const res = await postAPI.getPostSuggest();
        const posts: Post[] = res.list_post ?? [];
        setSuggestedPosts(posts);

        const uniqueCreators = Array.from(
          new Set(posts.map((p) => p.createdBy).filter(Boolean))
        );

        uniqueCreators.forEach(async (email) => {
          if (accountMap[email]) return;

          try {
            const acc = await AccountService.get_account_info(email);
            setAccountMap((prev) => ({
              ...prev,
              [email]: {
                fullName: acc.fullName,
                avatar: acc.avatar,
              },
            }));
          } catch (err) {
            console.error("Lỗi lấy account info:", email, err);
          }
        });
      } catch (err) {
        console.error("Lỗi lấy post suggest:", err);
      }
    };

    fetchSuggestedPosts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ================= FORMAT TIME =================
  const formatTimeAgo = (createdAt: string) => {
    const created = new Date(createdAt).getTime();
    const now = Date.now();
    const diffHours = Math.floor((now - created) / (1000 * 60 * 60));

    if (diffHours < 1) return "Vừa xong";
    if (diffHours < 24) return `${diffHours} giờ trước`;
    return `${Math.floor(diffHours / 24)} ngày trước`;
  };

  return (
    <div className="right-feed">
      <h4 className="feed-title">Trang bạn quan tâm</h4>

      {suggestedPosts.map((post) => {
        const account = accountMap[post.createdBy];

        return (
          <div key={post._id} className="feed-card">
            <div className="feed-header">
              <img
                src={account?.avatar || "/page-default.png"}
                alt={account?.fullName || post.createdBy}
                className="feed-avatar"
                onClick={() =>
                  navigate(`/profile/${post.createdBy || ""}`)
                }
                style={{ cursor: "pointer" }}
              />
              <div>
                <p
                  className="page-name"
                  onClick={() =>
                    navigate(`/profile/${post.createdBy || ""}`)
                  }
                  style={{ cursor: "pointer" }}
                >
                  {account?.fullName || post.createdBy}
                </p>
                <span className="time">
                  {formatTimeAgo(post.createdAt)}
                </span>
              </div>
            </div>

            <div className="feed-body">
              <p className="post-title">{post.title}</p>
              <p className="post-summary">
                {post.content.length > 80
                  ? post.content.slice(0, 80) + "..."
                  : post.content}
              </p>
            </div>

            <div className="feed-footer">
              <button
                className="btn-view"
                onClick={(e) => {
                  e.stopPropagation();
                  onOpenPostDetail(post);
                }}
              >
                Xem bài viết
              </button>
            </div>
          </div>
        );
      })}

      {suggestedPosts.length === 0 && (
        <p className="empty-feed">Chưa có bài viết gợi ý</p>
      )}
    </div>
  );
}
