import { useEffect, useState } from "react";
import "./reportHistory.css";
import { reportAPI } from "../../../../services/ReportService";

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

function ReportHistoryModal({ isOpen, onClose }: Props) {
  const [activeTab, setActiveTab] = useState<"mine" | "about">("mine");

  const [myReports, setMyReports] = useState<any[]>([]);
  const [aboutReports, setAboutReports] = useState<any[]>([]);

  const [loadingMine, setLoadingMine] = useState(false);
  const [loadingAbout, setLoadingAbout] = useState(false);

  const [expandedId, setExpandedId] = useState<string | null>(null);

  // ================== MY REPORTS ==================
  useEffect(() => {
    if (!isOpen || activeTab !== "mine") return;

    const fetchMyReports = async () => {
      try {
        setLoadingMine(true);
        const data = await reportAPI.getMyReport();
        setMyReports(data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingMine(false);
      }
    };

    fetchMyReports();
  }, [isOpen, activeTab]);

  // ================== ABOUT ME ==================
  useEffect(() => {
    if (!isOpen || activeTab !== "about") return;

    const fetchAboutReports = async () => {
      try {
        setLoadingAbout(true);
        const data = await reportAPI.getReportMe();

        const flat = (data || []).flatMap((group: any) =>
          (group.reports || []).map((r: any) => ({
            ...r,
            announciatorName: r.annunciatorName || group.announciators?.[0]?.name,
          }))
        );

        setAboutReports(flat);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingAbout(false);
      }
    };

    fetchAboutReports();
  }, [isOpen, activeTab]);

  // ================== STATUS MAP ==================
  const getStatus = (status: string | null | undefined) => {
    if (status === "approve") return "approved";
    if (status === "reject") return "rejected";
    return "pending";
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "approved":
        return "Đã xử lý";
      case "rejected":
        return "Đã từ chối";
      default:
        return "Đang xử lý";
    }
  };

  const toggleExpand = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  const formatDate = (dateStr: string) =>
    new Date(dateStr).toLocaleString("vi-VN");

  if (!isOpen) return null;

  return (
    <div className="report-modal-overlay" onClick={onClose}>
      <div
        className="report-history-modal-container"
        onClick={(e) => e.stopPropagation()}
      >
        {/* HEADER */}
        <div className="report-modal-header">
          <div className="title">Lịch sử báo cáo</div>
          <div className="close-btn" onClick={onClose}>
            ×
          </div>
        </div>

        {/* TABS */}
        <div className="report-tabs">
          <div
            className={`tab ${activeTab === "mine" ? "active" : ""}`}
            onClick={() => setActiveTab("mine")}
          >
            Báo cáo của tôi
          </div>

          <div
            className={`tab ${activeTab === "about" ? "active" : ""}`}
            onClick={() => setActiveTab("about")}
          >
            Báo cáo về tôi
          </div>
        </div>

        {/* CONTENT */}
        <div className="report-content">
          {/* ================== MINE ================== */}
          {activeTab === "mine" ? (
            loadingMine ? (
              <div>Đang tải...</div>
            ) : myReports.length === 0 ? (
              <div>Chưa có báo cáo nào</div>
            ) : (
              myReports.map((item) => {
                const status = getStatus(item.status);
                const isOpen = expandedId === item._id;

                return (
                  <div className="report-item-wrapper" key={item._id}>
                    <div className="report-item">
                      <div className="report-text">
                        Bạn đã báo cáo: <b>{item.violatorName}</b>
                      </div>

                      <div className="right-actions">
                        <div className={`report-status ${status}`}>
                          {getStatusText(status)}
                        </div>

                        <div
                          className="arrow-btn"
                          onClick={() => toggleExpand(item._id)}
                        >
                          {isOpen ? "▲" : "▼"}
                        </div>
                      </div>
                    </div>

                    {isOpen && (
                      <div className="report-detail">
                        <div>
                          <b>Lý do:</b> {item.description}
                        </div>
                        <div>
                          <b>Thời gian:</b>{" "}
                          {formatDate(item.reportedAt)}
                        </div>
                        <div>
                          <b>Nội dung:</b>{" "}
                          {item.content?.slice(0, 120)}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })
            )
          ) : (
            /* ================== ABOUT ME ================== */
            loadingAbout ? (
              <div>Đang tải...</div>
            ) : aboutReports.length === 0 ? (
              <div>Không có báo cáo nào về bạn</div>
            ) : (
              aboutReports.map((item) => {
                const status = getStatus(item.status);
                const isOpen = expandedId === item._id;

                return (
                  <div className="report-item-wrapper" key={item._id}>
                    <div className="report-item">
                      <div className="report-text">
                        <b>{item.annunciatorName}</b> đã báo cáo bạn
                      </div>

                      <div className="right-actions">
                        <div className={`report-status ${status}`}>
                          {getStatusText(status)}
                        </div>

                        <div
                          className="arrow-btn"
                          onClick={() => toggleExpand(item._id)}
                        >
                          {isOpen ? "▲" : "▼"}
                        </div>
                      </div>
                    </div>

                    {isOpen && (
                      <div className="report-detail">
                        <div>
                          <b>Lý do:</b> {item.description}
                        </div>
                        <div>
                          <b>Thời gian:</b>{" "}
                          {formatDate(item.reportedAt)}
                        </div>
                        <div>
                          <b>Nội dung:</b>{" "}
                          {item.content?.slice(0, 120)}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })
            )
          )}
        </div>
      </div>
    </div>
  );
}

export default ReportHistoryModal;