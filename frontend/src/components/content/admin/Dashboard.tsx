// components/content/admin/Dashboard.tsx
import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import styles from './AdminDashboard.module.css';
import axios from 'axios';

import { useNavigate } from 'react-router-dom';

const ApexChart = dynamic(() => import('react-apexcharts'), { ssr: false });

/* ------------- TYPE ------------- */
type TopPost = { postId: string; title: string; createdBy: string; interactions: number };
type TopReport = {
  typeContent: 'post' | 'account' | 'comment';
  contentId?: string;
  content?: string;
  violatorEmail: string;
  contentParentId?: string;
};

/* ------------- API ------------- */
const api = axios.create({ baseURL: 'http://localhost:8000' });
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/* ------------- COMPONENT ------------- */
const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const go = (path: string) => navigate(path);

  /* ---- state ---- */
  const [postToday, setPostToday] = useState<number>(0);
  const [reportToday, setReportToday] = useState<number>(0);
  const [complaintToday, setComplaintToday] = useState<number>(0);

  const [topPosts, setTopPosts] = useState<TopPost[]>([]);
  const [topReports, setTopReports] = useState<TopReport[]>([]);

  const [loading, setLoading] = useState<boolean>(true);

  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const showToast = (msg: string, ok: boolean) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 2500);
  };

  /* ---- fetch ---- */
  useEffect(() => {
    async function fetchAll() {
      try {
        const token = localStorage.getItem('token');

        const config = {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        };

        const [p, r, c, tp, tr] = await Promise.all([
          api.get('/post/get_post_of_day', config).then(res => res.data.data),
          api.get('/report/get_report_of_day', config).then(res => res.data.data),
          api.get('/complaint/get_complaint_of_day', config).then(res => res.data.data),
          api.get('/post/get_top_post', config).then(res => res.data.data),
          api.get('/report/get_top_report', config).then(res => res.data.data),
        ]);

        setPostToday(p);
        setReportToday(r);
        setComplaintToday(c);
        setTopPosts(tp);
        setTopReports(tr);

      } catch (e: any) {
        console.error('Fetch dashboard error', e.message);
        showToast("Lỗi tải dữ liệu", false);
      } finally {
        setLoading(false);
      }
    }
    fetchAll();
  }, []);

  /* ---- chart configs ---- */
  const interactChart = {
    options: {
      chart: {
        type: 'bar' as const,
        height: 360,
        toolbar: { show: false },
        events: {
          click: (_event: any, _chartContext: any, config: { dataPointIndex: any; }) => {
            const idx = config.dataPointIndex;
            if (idx === -1) return;           // clicked outside
            const postId = topPosts[idx]?.postId;
            if (postId) window.open(`/user/${postId}`, '_blank');
          },
        },
      },
      plotOptions: { bar: { horizontal: true, borderRadius: 4 } },
      dataLabels: { enabled: false },
      xaxis: {
        categories: topPosts.map((it) => `${it.title} (@${it.createdBy})`),
        axisBorder: { show: false },
        axisTicks: { show: false },
      },
      yaxis: { show: true },
      grid: { show: false },
      colors: ['#3366ff'],
    },
    series: [{ name: 'Tương tác', data: topPosts.map((it) => it.interactions) }],
  };

  const accountMap = new Map<string, number>();
  topReports.forEach((r) => {
    const email = r.violatorEmail;
    accountMap.set(email, (accountMap.get(email) || 0) + 1);
  });

  /* ---- chuyển thành 2 mảng song song ---- */
  const accountLabels = Array.from(accountMap.keys());
  const accountTotals = Array.from(accountMap.values());

  const complaintChart = {
    options: {
      chart: { type: 'bar' as const, height: 100, toolbar: { show: false } },
      plotOptions: { bar: { horizontal: true, borderRadius: 4 } },
      dataLabels: { enabled: false },
      xaxis: {
        categories: accountLabels, // chỉ còn email
        axisBorder: { show: false },
        axisTicks: { show: false },
      },
      yaxis: { show: true },
      grid: { show: false },
      colors: ['#ff3d71'],
    },
    series: [{ name: 'Tố cáo', data: accountTotals }],
  };

  /* ---- handler ---- */
  const sendAnnounce = async () => {
    if (topReports.length === 0) {
      showToast("Không có dữ liệu để gửi thông báo", false);
      return;
    }
    try {
      /* lấy danh sách violatorEmail duy nhất */
      const emails = [...new Set(topReports.map((r) => r.violatorEmail))];
      /* gọi API cho từng email (hoặc gọi bulk nếu backend có) */
      await Promise.all(
        emails.map((email) =>
          api.post('/announce/send_announce', { receiverEmail: email })
        )
      );
      showToast("Đã gửi thông báo!", true);
    } catch {
      showToast("Gửi thông báo thất bại", false);
    }
  };

  if (loading) return <p>Đang tải…</p>;

  return (
    <div className={styles.page}>
      {/* ---- stat cards ---- */}
      <div className={styles.grid4}>
        <div className={styles.clickableCard}>
          <StatCard title="Bài trong ngày" value={postToday} color="green" />
        </div>

        <div onClick={() => go('/admin/report')} className={styles.clickableCard}>
          <StatCard title="Đơn tố cáo" value={reportToday} color="purple" />
        </div>

        <div onClick={() => go('/admin/complaint')} className={styles.clickableCard}>
          <StatCard title="Đơn khiếu nại" value={complaintToday} color="orange" />
        </div>

        <div />
      </div>

      {/* ---- top posts ---- */}
      <section className={styles.statSection}>
        <h3 className={styles.statTitle}>Bài viết nổi bật trong tuần</h3>
        <div className={styles.chartBox} style={{ height: 360 }}>
          <ApexChart
            options={interactChart.options}
            series={interactChart.series}
            type="bar"
            height={360}
          />
        </div>
      </section>

      {/* ---- top reports ---- */}
      <section className={styles.statSection}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h3 className={styles.statTitle}>
            Nội dung bị tố cáo nhiều nhất trong ngày
          </h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ whiteSpace: 'nowrap', fontWeight: 500 }}>
              Thông báo nhắc nhở người dùng
            </span>

            <button
              onClick={sendAnnounce}
              title="Gửi thông báo"
              style={{
                background: '#ff3d71',
                border: 'none',
                borderRadius: 4,
                padding: '6px 8px',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'background 0.2s, transform 0.1s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#ff527d';
                e.currentTarget.style.transform = 'scale(1.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#ff3d71';
                e.currentTarget.style.transform = 'scale(1)';
              }}
              onMouseDown={(e) => (e.currentTarget.style.transform = 'scale(0.95)')}
              onMouseUp={(e) => (e.currentTarget.style.transform = 'scale(1.05)')}
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#fff"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
              </svg>
            </button>
          </div>
        </div>
        <div className={styles.chartBox} style={{ height: 360 }}>
          <ApexChart
            options={complaintChart.options}
            series={complaintChart.series}
            type="bar"
            height={360}
          />
        </div>
      </section>

      {toast && (
        <div
          className={`${styles.toast} ${
            toast.ok ? styles.toastOk : styles.toastErr
          }`}
        >
          {toast.msg}
        </div>
      )}
    </div>
  );
};

/* ---------- StatCard ---------- */
const StatCard: React.FC<{
  title: string;
  value: number | string;
  color: 'green' | 'purple' | 'pink' | 'red' | 'orange';
}> = ({ title, value, color }) => {
  const colorVar = {
    green: '#00d68f',
    purple: '#6c2486ff',
    pink: '#ff3d71',
    red: 'rgba(255,14,14,1)',
    orange: '#fa0',
  }[color];
  return (
    <div className={styles.card} style={{ borderLeft: `4px solid ${colorVar}` }}>
      <div className={styles.cardTitle}>{title}</div>
      <div className={styles.cardValue} style={{ color: colorVar }}>
        {typeof value === 'number' ? value.toLocaleString('vi-VN') : value}
      </div>
    </div>
  );
};

export default Dashboard;