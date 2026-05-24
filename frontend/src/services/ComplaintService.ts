import axiosInstance from "../utils/AxiosInstance";

export const complaintAPI = {
  addComplaint: (data: any) =>
    axiosInstance
      .post("/complaint/add_complaint", data)
      .then((res) => res.data),

  // Nếu sau này bạn muốn mở rộng thêm:
  // getAll: () =>
  //   axiosInstance.get("/complaint/get_all").then((res) => res.data),

  // getById: (id: string) =>
  //   axiosInstance.get(`/complaint/${id}`).then((res) => res.data),
};
