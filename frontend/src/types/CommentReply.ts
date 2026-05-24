export interface CommentReact {
  love: string[];
  like: string[];
  haha: string[];
  wow: string[];
  sad: string[];
  angry: string[];
}

export interface CommentReply {
  commentId: string;
  commentBy: string;
  postId: string;
  path: string;
  content: string;
  createdAt: string; // ⚠️ backend là datetime → frontend dùng string
  status: string;

  react?: CommentReact;

  thumbnails?: string[];
  thumbnails_url?: string[];
}