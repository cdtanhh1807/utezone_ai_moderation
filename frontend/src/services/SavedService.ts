import axiosInstance from "../utils/AxiosInstance";

export const savedAPI = {
  // Lấy danh sách collections theo email
  getCollections: (email: string) =>
    axiosInstance
      .get(`/post_saved/get_collections/${email}`)
      .then(res => res.data),

  // Tạo collection mới
  addCollection: (data: {
    collection_name: string;
  }) =>
    axiosInstance
      .post("/post_saved/add_collection", data)
      .then(res => res.data),

  // Thêm post vào collection
  addPostToCollection: (data: {
    collection_name: string;
    post_id: string;
  }) =>
    axiosInstance
      .post("/post_saved/add_post_to_collection", data)
      .then(res => res.data),

  // Xóa post khỏi collection
  removePostFromCollection: (data: {
   collection_name: string;
    post_id: string;
  }) =>
    axiosInstance
      .post("/post_saved/remove_post_from_collection", data)
      .then(res => res.data),

  // Xóa collection
  deleteCollection: (data: {
    collection_name: string;
  }) =>
    axiosInstance
      .post("/post_saved/delete_collection", data)
      .then(res => res.data),
};