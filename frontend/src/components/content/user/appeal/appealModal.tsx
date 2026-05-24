import React, { useState } from "react";
import "./appealModal.css";
import { complaintAPI } from "../../../../services/ComplaintService";
import { ToastService } from "../../../../services/ToastService";

interface AppealModalProps {
  isOpen: boolean;
  onClose: () => void;
  reportData: {
    content?: string | null;
    policyName?: string | null;
    contentAnnounce?: string | null;
    contentId?: string | null;
    contentParentId?: string | null;
    policyId?: string | null;
    type?: string | null;

    // ✅ THÊM
    approveBy?: string | null;      // email người duyệt
    approveAt?: string | Date | null; // thời điểm duyệt
  } | null;

  onSubmit?: (appealText: string) => void;
}

const AppealModal: React.FC<AppealModalProps> = ({
  isOpen,
  onClose,
  reportData,
  onSubmit,
}) => {
  const [appealText, setAppealText] = useState("");

  if (!isOpen || !reportData) return null;

  const handleSend = async () => {
    if (!appealText.trim()) {
      ToastService.warning("Vui lòng nhập lý do khiếu nại.");
      return;
    }

    console.log("Appeal text:", reportData);

    const payload = {
      policyId: reportData.policyId || "",
      typeContent: reportData.type || "",
      contentId: reportData.contentId || "",
      contentParentId: reportData.contentParentId || "",
      content: reportData.content || "",
      description: appealText.trim(),
      approveBy: reportData.approveBy || "",
      approveAt: reportData.approveAt || new Date(),
    };

    try {
      await complaintAPI.addComplaint(payload);
      ToastService.success("Khiếu nại của bạn đã được gửi thành công.");

      onSubmit && onSubmit(appealText); // nếu bạn còn muốn callback cũ

      setAppealText("");
      onClose();
    } catch (err) {
      console.error(err);
      ToastService.error("Gửi khiếu nại thất bại, vui lòng thử lại.");
    }
  };

  return (
    <div className="appealContainer" onClick={onClose}>
      <div className="appealModal" onClick={(e) => e.stopPropagation()}>
        <h3>Khiếu nại quyết định</h3>

        <div className="appealInfo">
          <p>
            <strong>Nội dung bị gỡ:</strong> {reportData.content}
          </p>
          <p>
            <strong>Chính sách vi phạm:</strong> {reportData.policyName}
          </p>
        </div>

        <textarea
          className="appealTextarea"
          placeholder="Nhập lý do bạn muốn khiếu nại..."
          value={appealText}
          onChange={(e) => setAppealText(e.target.value)}
        />

        <div className="appealActions">
          <button className="btn-cancel" onClick={onClose}>
            Hủy
          </button>
          <button className="btn-submit" onClick={handleSend}>
            Gửi khiếu nại
          </button>
        </div>
      </div>
    </div>
  );
};

export default AppealModal;
