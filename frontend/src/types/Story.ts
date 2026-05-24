export interface TextLayer {
  text: string;
  x: number;
  y: number;
  scale: number;
  rotate: number;
  color: string;
  font: string;
  fontSize: number;
  align: string;
  background?: string;
}

export interface VideoTrim {
  startAt: number;
  duration: number;
  hasOriginalSound: boolean;
}

export interface MusicInfo {
  name: string;
  fileid: string;
  url?: string;
  startAt: number;
  duration: number;
}

export interface ReactType {
  love: string[];
  like: string[];
  haha: string[];
  wow: string[];
  sad: string[];
  angry: string[];
}

export interface Story {
  _id: string;
  createdBy: string;
  createdAt: string;
  mediaType: "image" | "video";
  mediaUrls: string[];
  thumbnails?: string[];
  textLayers: TextLayer[];
  videoTrim?: VideoTrim;     // ⭐ THÊM
  music?: MusicInfo;
  react: ReactType;
  viewedBy: string[];
  status?: string;
}
