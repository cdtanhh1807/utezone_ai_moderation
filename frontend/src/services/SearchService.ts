// src/services/SearchService.ts
import axiosInstance from "../utils/AxiosInstance";

export const searchAPI = {
  searchAccount: (keySearch: string) =>
    axiosInstance
      .get(`/search/search_account/${encodeURIComponent(keySearch)}`)
      .then(res => res.data),

  searchPost: (keySearch: string) =>
    axiosInstance
      .get(`/search/search_post/${encodeURIComponent(keySearch)}`)
      .then(res => res.data),
};
