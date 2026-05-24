import axiosInstance from "../utils/AxiosInstance";

export const aiAPI = {
  summarizePost: (postId: string, forceRefresh: boolean = false) =>
    axiosInstance
      .post(`/ai/summarize_post/${postId}?force_refresh=${forceRefresh}`)
      .then((res) => res.data),
};