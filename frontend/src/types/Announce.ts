export interface Announce {
  id?: string;
  receiverEmail: string;
  senderEmail: string;
  type: "comment" | "report" | "complaint" | "account";
  contentAnnounce: string;
  isRead: boolean;
  createdAt: string; // hoặc Date nếu bạn muốn parse thành đối tượng Date
  contentId?: string;
  contentParentId?: string;
  content?: string;
  policyName?: string;
}

export interface GetAllAnnounceRequest {
  email: string;
}

export interface GetAllAnnounceResponse {
  data: Announce[];
  message?: string;
}
