import { GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";
import axiosInstance from "../../../../utils/AxiosInstance";
import AccountService from "../../../../services/AccountService";
import { useNavigate } from "react-router-dom";
import { ToastService } from "../../../../services/ToastService";
import "./GoogleLoginBtn.css";

interface BackendJwtPayload {
  sub: string;
  role: string;
  per: string;
  exp: number;
}

interface GoogleJwtPayload {
  sub: string;
  email?: string;
  name?: string;
  picture?: string;
}

export const GoogleLoginBtn = () => {
  const navigate = useNavigate();

  // ✅ Lấy redirect URL nếu có
  const params = new URLSearchParams(window.location.search);
  const redirectUrl = params.get("redirect");

  const handleSuccess = async (credentialResponse: any) => {
    try {
      // 1️⃣ Gửi google credential lên backend
      const loginRes = await axiosInstance.post("/account/google-login", {
        token: credentialResponse.credential,
      });

      const token = loginRes.data.access_token;

      // 2️⃣ Decode JWT từ BACKEND
      const decodedBackend = jwtDecode<BackendJwtPayload>(token);
      console.log("decoded login toan test:", decodedBackend);

      // 🚫 BLOCK LOGIN
      if (decodedBackend.per === "000") {
        ToastService.error("Tài khoản của bạn đã bị khóa");
        return;
      }

      // 🔥 Nếu có redirect → quay về hệ thống gọi login
      if (redirectUrl) {
        const separator = redirectUrl.includes("?") ? "&" : "?";
        window.location.href = `${redirectUrl}${separator}token=${token}`;
        return;
      }

      // ✅ OK → lưu token (chỉ khi login nội bộ)
      localStorage.setItem("token", token);

      // 3️⃣ Decode google token chỉ để lấy email
      const decodedGoogle: GoogleJwtPayload = jwtDecode(
        credentialResponse.credential
      );
      const email = decodedGoogle.email || decodedGoogle.sub;

      // 4️⃣ Lấy account info
      let accountData;
      try {
        accountData = await AccountService.get_account_info(email);
      } catch {
        navigate("/complete-profile");
        return;
      }

      if (accountData.fullName?.trim()) {
        navigate("/home", { state: { fromLogin: true } });
      } else {
        localStorage.setItem("account", JSON.stringify(accountData));
        navigate("/complete-profile");
      }
    } catch (err) {
      console.error("Google login failed:", err);
      ToastService.error("Đăng nhập Google thất bại");
    }
  };

  return (
    <GoogleLogin
      onSuccess={handleSuccess}
      onError={() => ToastService.error("Google Login Failed")}
    />
  );
};