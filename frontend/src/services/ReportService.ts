import axiosInstance from "../utils/AxiosInstance";

export const reportAPI = {
    sendReport: (data: any) =>
        axiosInstance
            .post("/report/send_report", data)
            .then((res) => res.data),

    getAllAnnounce: (content: string) =>
        axiosInstance
            .post("/policy/get_all_policy_content", { content })
            .then(res => res.data),

    approveReport: (data: any) =>
        axiosInstance
            .put("/report/approve_report", data)
            .then(res => res.data),

    getMyReport: () =>
        axiosInstance
            .get("/report/get_my_report")
            .then(res => res.data),
    getReportMe: () =>
        axiosInstance
            .get("/report/get_report_me")
            .then(res => res.data),
};