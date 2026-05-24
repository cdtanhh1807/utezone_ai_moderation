// ReportModal.tsx
import React, { useState, useEffect } from "react";
import "./reportModal.css";
import { motion, AnimatePresence } from "framer-motion";
import { reportAPI } from "../../../../services/ReportService";
import { ToastService } from "../../../../services/ToastService";

interface ReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  policy_type: "bài đăng" | "tài khoản" | "bình luận";
  type: "post" | "account" | "comment";
  violatorEmail?: string;
  content: string;
  contentId?: string;
  contentParentId?: string;
}

interface Policy {
  _id: string;
  name: string;
  description: string;
}

const policyViolations: Record<string, string[]> = {
  "Nội dung bài đăng": [
    "Đăng nội dung bạo lực hoặc ghê rợn",
    "Nội dung thù hận, phân biệt đối xử",
    "Đăng thông tin sai lệch hoặc tin giả",
    "Vi phạm pháp luật (ma túy, vũ khí...)",
    "Quấy rối hoặc spam",
  ],
  "Nội dung bình luận": [
    "Bình luận xúc phạm hoặc công kích cá nhân",
    "Bình luận kích động hoặc phân biệt đối xử",
    "Spam bình luận hoặc lặp lại nội dung",
  ],
  "Nội dung tin nhắn": [
    "Gửi tin nhắn quấy rối hoặc lăng mạ",
    "Tin nhắn lừa đảo hoặc chiếm đoạt thông tin",
    "Tin nhắn đe dọa, khuyến khích bạo lực",
    "Spam hoặc quảng cáo không được phép",
  ],
  "Bảo mật tài khoản": [
    "Truy cập trái phép vào tài khoản người khác",
    "Phishing hoặc chiếm đoạt tài khoản",
    "Hành vi đăng nhập bất thường",
  ],
};

const ReportModal = ({
  isOpen,
  onClose,
  policy_type,
  type,
  violatorEmail,
  content,
  contentId,
  contentParentId,
}: ReportModalProps) => {
  const [policy, setPolicy] = useState<Policy | null>(null);
  const [selectedAction, setSelectedAction] = useState("");
  const [customReason, setCustomReason] = useState("");

  useEffect(() => {
    if (isOpen) {
      reportAPI.getAllAnnounce(policy_type).then((data) => {
        const p = data.policy_list[0]; // backend chỉ trả về 1 policy
        setPolicy({
          _id: p._id,
          name: p.name,
          description: p.description,
        });
      });
    }
  }, [isOpen]);

  const handleSubmit = () => {
    const description = selectedAction || customReason;

    const payload = {
      violatorEmail,
      annunciatorEmail: "currentUser@example.com",
      typeContent: type,
      contentId,
      contentParentId,
      content,
      description,
      reportedAt: new Date(),
      check: false,
      policyId: policy?._id,
    };

    reportAPI.sendReport(payload).then(() => {
      ToastService.success("Tố cáo đã được gửi thành công.");
      setSelectedAction("");
      setCustomReason("");
      onClose();
    });
  };

  const violations = policy ? policyViolations[policy.name] || [] : [];

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div className="rp-modal-backdrop" onClick={onClose}>
          <motion.div
            className="report-modal-container"
            onClick={(e) => e.stopPropagation()}
          >
            <h2>Gửi tố cáo</h2>

            {policy && (
              <>
                <p>
                  <b>Chính sách áp dụng:</b> {policy.name}
                </p>
                <p className="policy-desc">{policy.description}</p>
              </>
            )}

            <p>Chọn hành vi vi phạm hoặc nhập mô tả:</p>
            <div className="report-actions">
              {violations.map((v) => (
                <label key={v}>
                  <input
                    type="radio"
                    name="action"
                    value={v}
                    checked={selectedAction === v}
                    onChange={() => setSelectedAction(v)}
                    disabled={customReason.trim().length > 0} // disable radio nếu có nhập customReason
                  />
                  {v}
                </label>
              ))}

              <div className="custom-reason">
                <input
                  type="text"
                  placeholder="Mô tả khác..."
                  value={customReason}
                  onChange={(e) => setCustomReason(e.target.value)}
                  onFocus={() => setSelectedAction("")} // khi focus vào ô thì bỏ radio đã chọn
                />
              </div>
            </div>

            <div className="modal-footer">
              <button className="cancel-btn" onClick={onClose}>
                Hủy
              </button>
              <button
                className="submit-btn"
                disabled={!selectedAction && !customReason}
                onClick={handleSubmit}
              >
                Gửi tố cáo
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default ReportModal;
