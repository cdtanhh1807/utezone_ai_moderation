import { useEffect, useState } from "react";
import "./profileArchived.css";
import { postAPI } from "../../../../services/PostService";
import { jwtDecode } from "jwt-decode";
import type { Post } from "../../../../types/Post";
import ProfilePosts from "./profilePost";

interface JwtPayload {
  sub: string; // email
}

function ProfileArchived() {
  const [postArchives, setPostArchives] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) throw new Error("Không có token");

        const decoded: JwtPayload = jwtDecode<JwtPayload>(token);
        const currentUserEmail = decoded.sub;

        console.log("Email user:", currentUserEmail);

        const res = await postAPI.getByEmail(currentUserEmail);
        const posts: Post[] = res.post_list;

        console.log("Post theo email:", posts);

        const archivedPosts = posts
          .filter((post) => post.status === "off")
          .sort(
            (a, b) =>
              new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
          );

        console.log("Bài viết đã lưu trữ:", archivedPosts);

        setPostArchives(archivedPosts);
      } catch (error) {
        console.error("Lỗi khi lấy dữ liệu:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="archive-container">
      <ProfilePosts archive={true} />
    </div>
  );
}

export default ProfileArchived;
