import {
  Routes,
  Route,
  NavLink,
  Navigate,
  useNavigate,
} from 'react-router-dom';
import {
  FiBarChart2,
  FiUsers,
  FiAlertTriangle,
  FiClock,
  FiSlash,
  FiMessageSquare,
  FiFileText,
  FiLogOut,
} from 'react-icons/fi';
import styles from './AdminDashboard.module.css';
import AccountManager from './AccountManager';
import PolicyManager from './PolicyManager';
import ReportManager from './ReportManager';
import BanManager from './BanManager';
import ComplaintManager from './ComplaintManager';
import Dashboard from './Dashboard';
import ApproveHistory from './ApproveHistory';
import IncidentReportManager from './IncidentReportManager';
import { FiAlertOctagon } from 'react-icons/fi'; 

const SideBar: React.FC = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  const navs = [
    { to: '/admin', label: 'Thống kê', icon: <FiBarChart2 />, end: true },
    { to: '/admin/account', label: 'Tài khoản', icon: <FiUsers /> },
    { to: '/admin/report', label: 'Tố cáo', icon: <FiAlertTriangle /> },
    { to: '/admin/approve_history', label: 'Lịch sử kiểm duyệt', icon: <FiClock /> },
    { to: '/admin/ban', label: 'Chặn', icon: <FiSlash /> },
    { to: '/admin/complaint', label: 'Khiếu nại', icon: <FiMessageSquare /> },
    { to: '/admin/policy', label: 'Chính sách', icon: <FiFileText /> },
    { to: '/admin/incident_report', label: 'Báo cáo sự cố', icon: <FiAlertOctagon /> },
  ];
  return (
    <aside className={styles.sideBar}>
      <h2 className={styles.logo}>UTE Zone</h2>

      <nav className={styles.navWrap}>
        {navs.map((n) => (
          <NavLink
            key={n.to}
            to={n.to}
            end={n.end}
            className={({ isActive }) =>
              isActive ? styles.navActive : styles.navLink
            }
          >
            <span className={styles.navIcon}>{n.icon}</span>
            <span>{n.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Nút Đăng xuất */}
      <div className={styles.logoutBox}>
        <button className={styles.logoutBtn} onClick={handleLogout}>
          <FiLogOut className={styles.navIcon} />
          <span>Đăng xuất</span>
        </button>
      </div>
    </aside>
  );
};

const TopBar: React.FC = () => (
  <header className={styles.topBar}>
    <span className={styles.breadcrumb}>Trang quản trị</span>
    <div className={styles.user}>Admin</div>
  </header>
);

const AdminDashboard: React.FC = () => (
  <div className={styles.wrapper}>
    <SideBar />
    <div className={styles.main}>
      <TopBar />
      <div className={styles.content}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/account" element={<AccountManager />} />
          <Route path="/ban" element={<BanManager />} />
          <Route path="/report" element={<ReportManager />} />
          <Route path="/approve_history" element={<ApproveHistory />} />
          <Route path="/policy" element={<PolicyManager />} />
          <Route path="/complaint" element={<ComplaintManager />} />
          <Route path="/incident_report" element={<IncidentReportManager />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>  
  </div>
);

export default AdminDashboard;