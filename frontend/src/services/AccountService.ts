import axiosInstance from "../utils/AxiosInstance";
import type { UserInfo } from "../types/Account";

export interface FollowBlockRequest {
  owner: string;
  client: string;
}

export interface FollowBlockResponse {
  message: boolean;
}

export interface GetRelationResponse {
  followers?: string[];
  followed?: string[];
  blocks?: string[];
}

// ===== NEW TYPES =====
export interface SuggestFollowRequest {
  limit?: number;
}

export interface SuggestFollowItem {
  id: string;
  email: string;
  fullName?: string;
  department?: string;
  avatar?: string;
  description?: string;
  interaction_score?: number;
  posts_count?: number;
  comments_count?: number;
}

export interface SuggestFollowResponse {
  suggestions: SuggestFollowItem[];
}

const AccountService = {
  // ===== EXISTING METHODS =====

  get_account_info: (email?: string) =>
    axiosInstance
      .get("/account/account_info", {
        params: email ? { email: decodeURIComponent(email) } : {},
      })
      .then((res) => res.data),

  logout: (token: string) =>
    axiosInstance
      .post("/account/logout", null, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        params: {
          token_in: token,
        },
      })
      .then((res) => res.data),

  updateProfile: async (data: Partial<UserInfo>) => {
    const res = await axiosInstance.put("/account/update_account", data);
    return res.data;
  },

  follow: async (data: FollowBlockRequest): Promise<FollowBlockResponse> => {
    const res = await axiosInstance.put("/account/follow", data);
    return res.data;
  },

  un_follow: async (data: FollowBlockRequest): Promise<FollowBlockResponse> => {
    const res = await axiosInstance.put("/account/un_follow", data);
    return res.data;
  },

  block: async (data: FollowBlockRequest): Promise<FollowBlockResponse> => {
    const res = await axiosInstance.put("/account/block", data);
    return res.data;
  },

  un_block: async (data: FollowBlockRequest): Promise<FollowBlockResponse> => {
    const res = await axiosInstance.put("/account/un_block", data);
    return res.data;
  },

  get_account_relation: async (
    email: string
  ): Promise<GetRelationResponse> => {
    const res = await axiosInstance.get(
      `/account/account_relation/${encodeURIComponent(email)}`
    );
    return res.data;
  },

  get_mod: async () => {
    const res = await axiosInstance.get("/account/get_mod");
    return res.data;
  },

  // ===== NEW API =====
  get_suggest_follow: async (
    data: SuggestFollowRequest
  ): Promise<SuggestFollowResponse> => {
    const res = await axiosInstance.get("/account/suggest_follow", {
      params: {
        limit: data.limit,
        // ❗ email KHÔNG cần gửi vì BE lấy từ token
      },
    });
    return res.data;
  },
};

export default AccountService;