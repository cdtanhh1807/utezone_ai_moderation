import React from "react";
import { useNavigate } from "react-router-dom";
import "./welcomePage.css";

// SVG Icons đơn giản để không cần cài thêm thư viện
const ArrowRightIcon = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <line x1="5" y1="12" x2="19" y2="12"></line>
    <polyline points="12 5 19 12 12 19"></polyline>
  </svg>
);

const CodeIcon = () => (
  <svg
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polyline points="16 18 22 12 16 6"></polyline>
    <polyline points="8 6 2 12 8 18"></polyline>
  </svg>
);

const UsersIcon = () => (
  <svg
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
    <circle cx="9" cy="7" r="4"></circle>
    <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
  </svg>
);

const WelcomePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="ute-container">
      {/* Background decoration */}
      <div className="bg-grid-pattern"></div>

      {/* Header / Navigation */}
      <header className="ute-header">
        <div className="ute-logo">
          <span className="logo-icon">
            <CodeIcon />
          </span>
          <span className="logo-text">UTEzone</span>
        </div>
        <nav className="ute-nav">
          <button className="btn-ghost" onClick={() => navigate("/login")}>
            Đăng nhập
          </button>
          <button
            className="btn-primary-sm"
            onClick={() => navigate("/signup")}
          >
            Đăng ký
          </button>
        </nav>
      </header>

      {/* Main Hero Section */}
      <main className="ute-main">
        <div className="hero-badge">
          <span>🚀 Dành cho sinh viên và giảng viên HCMUTE</span>
        </div>

        <h1 className="hero-title">
          Nơi <span className="highlight-text">Công Nghệ</span> <br />
          là sự Kết Nối.
        </h1>

        <p className="hero-subtitle">
          Đây là diễn đàn lý tưởng dành cho sinh viên HCMUTE. Chia sẻ kiến ​​thức,
          và kết nối với thế hệ kỹ sư tương lai.
        </p>

        <div className="hero-actions">
          <button
            className="btn-primary-lg"
            onClick={() => navigate("/signup")}
          >
            Bắt đầu <ArrowRightIcon />
          </button>
          <button
            className="btn-secondary-lg"
            onClick={() => navigate("/login")}
          >
            Đăng nhập
          </button>
        </div>

        {/* Feature Highlights (Optional but adds value) */}
        <div className="hero-features">
          <div className="feature-item">
            <div className="feature-icon">
              <CodeIcon />
            </div>
            <p>Trao đổi học thuật</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">
              <UsersIcon />
            </div>
            <p>Kết nối cộng đồng</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">📚</div>
            <p>Thông tin</p>
          </div>
        </div>
      </main>

      <footer className="ute-footer">
        <p>© 2025 UTEzone. Built for students, by students.</p>
      </footer>
    </div>
  );
};

export default WelcomePage;
