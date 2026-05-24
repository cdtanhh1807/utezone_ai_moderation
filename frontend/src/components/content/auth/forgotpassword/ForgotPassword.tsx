import { useState, type ChangeEvent, type FormEvent } from 'react';
import axiosInstance from '../../../../utils/AxiosInstance';
import { Link, useNavigate } from 'react-router-dom';
import logo_truong from "../../../../assets/logo_login.png";
import logo from "../../../../assets/logo.png";
import './ForgotPassword.css';

type ForgotPasswordForm = {
    email: string;
    otp: string;
    newPassword: string;
}

type OtpResponse = {
    message: string;
}

function ForgotPassword() {
    const [formData, setFormData] = useState<ForgotPasswordForm>({
        email: '',
        otp: '',
        newPassword: ''
    });

    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);

    const navigate = useNavigate();

    const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            const response = await axiosInstance.post<OtpResponse>(
                '/account/forgot-password',
                {
                    email: formData.email,
                    otp: formData.otp,
                    new_password: formData.newPassword
                }
            );

            console.log(response.data.message);
            navigate('/verify-forgot-password', { state: { email: formData.email } });
        } catch (err: any) {
            if (err.response) {
                setError(err.response.data?.detail || 'Không thể gửi yêu cầu, vui lòng thử lại');
            } else {
                setError('Không thể kết nối đến server. Vui lòng kiểm tra lại kết nối hoặc backend.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="forgot-container">
            <div className="forgot-left">
                <img
                    src={logo_truong}
                    alt="Forgot Password Illustration"
                    className="forgot-image"
                />
            </div>
            <div className="forgot-right">
                <img
                    src={logo}
                    alt="Forgot Password Logo"
                    className="forgot-logo-image"
                />
                <form onSubmit={handleSubmit}>
                    <input
                        type="email"
                        name="email"
                        placeholder="Nhập email của bạn"
                        value={formData.email}
                        onChange={handleChange}
                        required
                    />
                    <button type="submit" disabled={isLoading} className="login-btn">
                        {isLoading ? 'Đang gửi...' : 'Gửi OTP'}
                    </button>
                    {error && <div className="error-message">{error}</div>}

                    <div className="login-links">
                        <p><Link to="/login">Quay lại đăng nhập</Link></p>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default ForgotPassword;
