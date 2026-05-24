import { useLocation, useNavigate, Navigate } from "react-router-dom";
import { useState, type FormEvent, type ChangeEvent } from "react";
import { AxiosError } from "axios";
import axiosInstance from "../../../../utils/AxiosInstance";
import { isTokenExpired } from '../../../../utils/Auth';
import otpImage from "../../../../assets/logo_login.png"; // ảnh bên trái
import logo from "../../../../assets/logo.png"; // logo trên form
import './OtpForgotPassword.css';

const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

function validatePassword(password: string): string | null {
    if (!passwordRegex.test(password)) {
        return "Mật khẩu phải >= 8 ký tự, có chữ hoa, chữ thường, số và ký tự đặc biệt.";
    }
    return null;
}

function OtpForgotPassword() {
    const location = useLocation();
    const navigate = useNavigate();

    const email = (location.state as { email: string })?.email;
    const [otp, setOtp] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const token = localStorage.getItem('token');
    if (token && !isTokenExpired(token)) {
        return <Navigate to="/" replace />;
    }

    const handleChangePassword = (e: ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        if (name === "password") setPassword(value);
        if (name === "confirmPassword") setConfirmPassword(value);
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        if (password !== confirmPassword) {
            setError("Mật khẩu và xác nhận mật khẩu không khớp");
            setIsLoading(false);
            return;
        }

        const passwordErr = validatePassword(password);
        if (passwordErr) {
            setError(passwordErr);
            setIsLoading(false);
            return;
        }

        try {
            const response = await axiosInstance.post<{ message: string }>(
                "/account/change-password/",
                { email, otp, new_password: password }
            );

            console.log(response.data.message);
            navigate("/login");

        } catch (err) {
            const error = err as AxiosError<{ message: string }>;
            const msg = error.response?.data?.message || "OTP không đúng hoặc đã hết hạn.";
            setError(msg);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="otp-container">
            <div className="otp-left">
                <img src={otpImage} alt="OTP Illustration" className="otp-image" />
            </div>
            <div className="otp-right">
                <img src={logo} alt="Logo" className="otp-logo" />
                <h2>Xác minh OTP & Đặt lại mật khẩu</h2>
                <p>Chúng tôi đã gửi mã OTP tới email: <b>{email}</b></p>
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        placeholder="Nhập OTP"
                        value={otp}
                        onChange={e => setOtp(e.target.value)}
                        required
                    />
                    <input
                        type="password"
                        name="password"
                        placeholder="Mật khẩu mới"
                        value={password}
                        onChange={handleChangePassword}
                        required
                    />
                    <input
                        type="password"
                        name="confirmPassword"
                        placeholder="Xác nhận mật khẩu mới"
                        value={confirmPassword}
                        onChange={handleChangePassword}
                        required
                    />
                    <button type="submit" disabled={isLoading} className="otp-btn">
                        {isLoading ? "Đang xác minh..." : "Đổi mật khẩu"}
                    </button>
                    {error && <div className="error-message">{error}</div>}
                    <div className="otp-links">
                        <p>Quay lại <b><a href="/login">đăng nhập</a></b></p>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default OtpForgotPassword;
