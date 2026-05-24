import axiosInstance from "../utils/AxiosInstance";
import type { CommentReply } from "../types/CommentReply";

export interface UpdateCommentStatusRequest {
  commentId: string;
  statusComment: string;
}
export interface UpdateCommentReplyStatusRequest {
  postId: string;
  commentId: string;
  path: string;
  status: "active" | "hidden";
}
export interface UpdatePostResponse {
  post: any;
}

export interface AddCommentReplyRequest {
  postId: string;
  parentId?: string;
  path?: string;
  content: string;
  thumbnails?: string[];
}

// Request lấy reply
export interface GetCommentReplyRequest {
  postId: string;
  parentId: string;
}

// ✅ Response React cho comment / reply
export interface UpdateCommentReactResponse {
  message: string;
  react: Record<string, string[]>;
}
interface AddCommentPayload {
  postId: string;
  content: string;
  thumbnails?: string[]; // 👈 thêm dòng này
}


const CommentService = {
  // ✅ Comment gốc
  addComment: (data: AddCommentPayload) =>
    axiosInstance.post("/comment/add_comment", data).then((res) => res.data),

  // ✅ Lấy comment theo post
  getByPostId: (postId: string) =>
    axiosInstance.get(`/comment/get_by_post/${postId}`).then((res) => res.data),

  // ✅ React comment chính
  updateCommentReact: (id: string, comment_id: string, react_type: string) =>
    axiosInstance
      .put(`/comment/${id}/comments/${comment_id}/react/${react_type}`)
      .then((res) => res.data),

  // ✅ Update status comment chính
  updateCommentStatus: (
    postId: string,
    data: UpdateCommentStatusRequest
  ): Promise<UpdatePostResponse> =>
    axiosInstance.put(`/post/update_comment/${postId}`, data).then((res) => res.data),

  // ✅ Thêm reply
  addCommentReply: (data: AddCommentReplyRequest) =>
    axiosInstance.post("/comment/add_comment_reply", data).then((res) => res.data),

  // ✅ Lấy reply theo parentId
  getCommentReply: (data: { postId: string; parentId: string }) =>
    axiosInstance.post("/comment/get_comment_reply", data).then((res) => res.data),

  // 🔹 MỚI: update status reply
  updateStatusCommentReply: (data: UpdateCommentReplyStatusRequest) =>
  axiosInstance
    .put("/comment/update_status_comment_reply", data)
    .then((res) => res.data),
  // 🔹 MỚI: react cho reply
  updateCommentReplyReact: (
    postId: string,
    commentId: string,
    reactType: string
  ): Promise<UpdateCommentReactResponse> =>
    axiosInstance
      .put(`/comment/${postId}/comment_reply/${commentId}/react/${reactType}`)
      .then((res) => res.data),
};

export default CommentService;