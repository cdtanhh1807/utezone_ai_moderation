import React, { useEffect, useState } from "react";
import { announceAPI } from "../../../../services/AnnounceService";
import AccountService from "../../../../services/AccountService";
import { postAPI } from "../../../../services/PostService";
import "./notificationModal.css";
import { jwtDecode } from "jwt-decode";
import AppealModal from "../appeal/appealModal";
import ComplaintModal from "./complaintModal";
import logoht from "../../../../assets/logo_he_thong.jpg";

interface Announce {
  _id: string;
  senderEmail: string;
  type: string;
  contentAnnounce: string;
  createdAt: string;
  contentId?: string; // commentId
  contentParentId?: string; // postId
}

interface SenderInfo {
  fullName: string;
  avatar: string;
}

interface NotificationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenPostDetail: (post: any, commentId?: string | null) => void;
}

const NotificationModal: React.FC<NotificationModalProps> = ({
  isOpen,
  onClose,
  onOpenPostDetail,
}) => {
  const [notifications, setNotifications] = useState<Announce[]>([]);
  const [senderInfoMap, setSenderInfoMap] = useState<
    Record<string, SenderInfo>
  >({});
  const [loading, setLoading] = useState(false);

  // =========================
  // APPEAL MODAL
  // =========================
  const [isAppealModalOpen, setIsAppealModalOpen] = useState(false);
  const [selectedReport, setSelectedReport] = useState<Announce | null>(null);

  // =========================
  // COMPLAINT MODAL
  // =========================
  const [isComplaintModalOpen, setIsComplaintModalOpen] = useState(false);
  const [complaintContent, setComplaintContent] = useState<string | null>(null);

  // =========================
  // SYSTEM MODAL
  // =========================
  const [isSystemModalOpen, setIsSystemModalOpen] = useState(false);
  const [systemContent, setSystemContent] = useState("");

  // =========================
  // CURRENT USER EMAIL
  // =========================
  const token = localStorage.getItem("token");
  let currentUserEmail: string | null = null;

  if (token) {
    try {
      const decoded = jwtDecode<{ sub: string }>(token);
      currentUserEmail = decoded.sub;
    } catch {}
  }

  // =========================
  // FETCH NOTIFICATIONS
  // =========================
  useEffect(() => {
    if (!isOpen) return;

    setLoading(true);

    announceAPI.getAllAnnounce().then(async (res) => {
      const list: Announce[] = (res.announce_list || []).filter(
        (item: Announce) => item.senderEmail !== currentUserEmail
      );

      setNotifications(list.reverse());

      const senderEmails = Array.from(
        new Set<string>(list.map((item) => item.senderEmail))
      );

      const infoMap: Record<string, SenderInfo> = {};

      await Promise.all(
        senderEmails.map(async (email: string) => {
          try {
            const acc = await AccountService.get_account_info(email);
            infoMap[email] = {
              fullName: acc.fullName,
              avatar: acc.avatar,
            };
          } catch {
            infoMap[email] = { fullName: email, avatar: "" };
          }
        })
      );

      setSenderInfoMap(infoMap);
      setLoading(false);
    });
  }, [isOpen, currentUserEmail]);

  if (!isOpen) return null;

  // =========================
  // CLICK NOTIFICATION
  // =========================
  const handleNotificationClick = async (item: Announce) => {
    // Complaint
    if (item.type === "complaint") {
      setComplaintContent(item.contentAnnounce);
      setIsComplaintModalOpen(true);
      return;
    }

    // Report
    if (item.type === "report") {
      setSelectedReport(item);
      setIsAppealModalOpen(true);
      return;
    }

    // Account/system notification
    if (item.type === "account") {
      setSystemContent(item.contentAnnounce);
      setIsSystemModalOpen(true);
      return;
    }

    try {
      // Post
      if (item.type === "post" && item.contentId) {
        const res = await postAPI.getById(item.contentId);
        onClose();
        onOpenPostDetail(res.post || res, null);
        return;
      }

      // Comment
      if (item.type === "comment" && item.contentParentId) {
        const res = await postAPI.getById(item.contentParentId);
        onClose();
        onOpenPostDetail(res.post || res, item.contentId);
        return;
      }
    } catch (err) {
      console.error("❌ Không mở được PostDetail:", err);
    }
  };

  return (
    <>
      <div className="notificationContainer" onClick={onClose}>
        <div className="notificationModal" onClick={(e) => e.stopPropagation()}>
          <h3>Thông báo</h3>

          {loading && <p>Đang tải...</p>}

          {!loading &&
            notifications.map((item) => {
              const sender = senderInfoMap[item.senderEmail];

              return (
                <div
                  key={item._id}
                  className="notificationItem"
                  onClick={() => handleNotificationClick(item)}
                >
                  {sender?.avatar && (
                    <img
                      src={sender.avatar}
                      alt={sender.fullName}
                      className="notificationAvatar"
                    />
                  )}
                  {!sender?.avatar && (
                    <img
                      src={logoht}
                      className="notificationAvatar"
                    />
                  )}

                  <div className="notificationContent">
                    <p>{item.contentAnnounce}</p>
                    <span>{new Date(item.createdAt).toLocaleString()}</span>
                  </div>
                </div>
              );
            })}
        </div>
      </div>

      {/* Complaint Modal */}
      <ComplaintModal
        isOpen={isComplaintModalOpen}
        content={complaintContent}
        onClose={() => setIsComplaintModalOpen(false)}
      />

      {/* Appeal Modal */}
      <AppealModal
        isOpen={isAppealModalOpen}
        reportData={selectedReport}
        onClose={() => setIsAppealModalOpen(false)}
      />

      {/* System Modal */}
      {isSystemModalOpen && (
        <div
          className="systemModalBackdrop"
          onClick={() => setIsSystemModalOpen(false)}
        >
          <div
            className="systemModalContent"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="systemModalTitle">Hệ thống thông báo</h2>
            <p className="systemModalBody">{systemContent}</p>
            <div className="systemModalFooter">
              <button onClick={() => setIsSystemModalOpen(false)}>Đóng</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default NotificationModal;
