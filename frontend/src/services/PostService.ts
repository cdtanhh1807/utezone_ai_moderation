import axiosInstance from "../utils/AxiosInstance";

export const postAPI = {
  getAll: () =>
    axiosInstance.get('/post/get_all_post').then((res) => res.data),
  
  getPostSuggest: () =>
    axiosInstance.get('/post/get_post_suggest').then((res) => res.data),
    
  getById: (id: string) =>
    axiosInstance.get(`/post/get_post/${id}`).then((res) => res.data),

  updatePost: (id: string, data: any) =>
    axiosInstance.put(`/post/update_post/${id}`, data).then((res) => res.data),

  updateReact: (id: string, react_type: string) =>
    axiosInstance.put(`/post/posts/${id}/react/${react_type}`).then((res) => res.data),

  addPost: (data: any) =>
    axiosInstance.post(`/post/add_post`, data).then(res => res.data),

  getByEmail: (email: string) =>
    axiosInstance.get(`/post/get_post_by_email/${encodeURIComponent(email)}`).then(res => res.data),

  deletePost: (id: string) =>
    axiosInstance.delete(`/post/delete_post/${id}`).then(res => res.data),

  sharePost: (postId: string, data: any) =>
    axiosInstance.post(`/post/share_post/${postId}`, data).then(res => res.data),

  getPostHidden: () =>
    axiosInstance.get('/post/get_post_hidden_by_email').then((res) => res.data),
};
