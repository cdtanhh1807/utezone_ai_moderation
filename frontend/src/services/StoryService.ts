import axiosInstance from "../utils/AxiosInstance";

export const StoryService = {
  getAllActive: () =>
    axiosInstance.get('/story/active').then(res => res.data),

  getByUser: (userId: string) =>
    axiosInstance.get(`/story/user/${userId}`).then(res => res.data),

  addStory: (data: any) =>
    axiosInstance.post('/story/add_story', data).then(res => res.data),

  // ⭐ NEW: lấy story theo từng user trong ngày
  getTodayStories: () =>
    axiosInstance.get('story/get_today_story').then(res => res.data),

  // ⭐ NEW: xóa story theo story_id
  deleteStory: (storyId: string) =>
    axiosInstance
      .delete(`/story/delete_story/${storyId}`)
      .then(res => res.data)
      .catch(err => {
        console.error("Delete story error:", err);
        throw err;
      }),
};
