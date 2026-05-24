import { useState, type ChangeEvent, type FormEvent } from "react";
import axiosInstance from "../../../../utils/AxiosInstance";
import { Link, useNavigate } from "react-router-dom";
import { GoogleLoginBtn } from "../google/GoogleLoginBtn";
import logo_truong from "../../../../assets/logo_login.png";
import logo from "../../../../assets/logo.png";
import { jwtDecode } from "jwt-decode";
import { ToastService } from "../../../../services/ToastService";
import AccountService from "../../../../services/AccountService";

import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import VisibilityOffOutlinedIcon from "@mui/icons-material/VisibilityOffOutlined";

import "./Login.css";

type LoginForm = {
  username: string;
  password: string;
};

type LoginResponse = {
  access_token: string;
  token_type: string;
};

function Login() {
  const [formData, setFormData] = useState<LoginForm>({
    username: "",
    password: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const navigate = useNavigate();

  // ✅ Lấy redirect URL nếu có
  const params = new URLSearchParams(window.location.search);
  const redirectUrl = params.get("redirect");

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    const payload = new URLSearchParams();
    payload.append("username", formData.username);
    payload.append("password", formData.password);

    try {
      const response = await axiosInstance.post<LoginResponse>(
        "/account/login",
        payload,
        {
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
        }
      );

      const token = response.data.access_token;

      interface JwtPayload {
        sub: string;
        role: string;
        per: string;
        exp: number;
      }

      const decoded = jwtDecode<JwtPayload>(token);
      console.log("decoded login:", decoded);

      // 🚫 Block login
      if (decoded.per === "000") {
        ToastService.error("Tài khoản của bạn đã bị khóa");
        return;
      }

      // 🔥 Nếu có redirect → quay về hệ thống gọi login
      if (redirectUrl) {
        const separator = redirectUrl.includes("?") ? "&" : "?";
        window.location.href = `${redirectUrl}${separator}token=${token}`;
        return;
      }

      // ✅ lưu token (chỉ khi login nội bộ)
      localStorage.setItem("token", token);

      // 🟥 Admin
      if (decoded.role === "Administrator") {
        navigate("/admin");
        return;
      }

      // 🟩 User
      let accountData;
      try {
        accountData = await AccountService.get_account_info(decoded.sub);
      } catch {
        navigate("/complete-profile");
        return;
      }

      if (!accountData.fullName?.trim()) {
        localStorage.setItem("account", JSON.stringify(accountData));
        navigate("/complete-profile");
        return;
      }

      navigate("/home");
    } catch (err: any) {
      if (err.response?.status === 401) {
        setError("Sai tên đăng nhập hoặc mật khẩu");
      } else {
        setError("Không thể kết nối đến server");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-left">
        <img
          src={logo_truong}
          alt="Login Illustration"
          className="login-image"
        />
      </div>

      <div className="login-right">
        <img src={logo} alt="Logo" className="login-utezone-image" />

        <form onSubmit={handleSubmit}>
          <input
            type="text"
            name="username"
            placeholder="Tên đăng nhập"
            value={formData.username}
            onChange={handleChange}
            required
          />

          <div className="password-wrapper">
            <input
              type={showPassword ? "text" : "password"}
              name="password"
              placeholder="Mật khẩu"
              value={formData.password}
              onChange={handleChange}
              required
            />

            <span
              className="toggle-password"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? (
                <VisibilityOffOutlinedIcon />
              ) : (
                <VisibilityOutlinedIcon />
              )}
            </span>
          </div>

          <button type="submit" disabled={isLoading} className="login-btn">
            {isLoading ? "Đang đăng nhập..." : "Đăng nhập"}
          </button>

          {error && <div className="error-message">{error}</div>}

          <div className="social-login">
            <GoogleLoginBtn />
          </div>

          <div className="login-links">
            <div className="forgot_password">
              <p className="qmk">
                <Link to="/forgot-password">Quên mật khẩu?</Link>
              </p>
            </div>

            <div className="btn_signup">
              <p>
                Chưa có tài khoản? <Link to="/signup">Đăng ký</Link>
              </p>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Login;