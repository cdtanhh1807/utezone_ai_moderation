// src/services/FileService.ts
import axiosInstance from "../utils/AxiosInstance";

export interface UploadResponse {
  file_id: string;
  url: string;
}

export interface FileUrlResponse {
  url: string;
}

const FileService = {
  uploadPicture: (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    return axiosInstance
      .post("/file/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((res) => res.data as UploadResponse);
  },

  getFileUrl: (fileId: string) => {
    // 👇 chỉ build URL trực tiếp
    return `${axiosInstance.defaults.baseURL}/file/${fileId}`;
  },
};

export default FileService;