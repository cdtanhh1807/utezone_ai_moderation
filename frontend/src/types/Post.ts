export interface ReactType {
  love: string[];
  like: string[];
  haha: string[];
  wow: string[];
  sad: string[];
  angry: string[];
}

export interface CommentReact {
  love: string[];
  like: string[];
  haha: string[];
  wow: string[];
  sad: string[];
  angry: string[];
}

export interface Comment {
  commentId: string;
  commentBy: string;
  content: string;
  reacts: CommentReact;
  createdAt: string;
  statusComment: string;
  thumbnails?: string[];
}

export interface Post {
  _id: string;
  title: string;
  content: string;
  createdAt: string;
  postType: string;
  visibility: string;
  status: string;
  createdBy: string;
  category?: string[];
  views: number;
  react?: ReactType;
  pollData?: any;
  comments?: Comment[];
  lastEdited?: string;
  thumbnails?: string[];
  thumbnails_url: string[];
  ai_summary?: string;
  postId?: string;
}
