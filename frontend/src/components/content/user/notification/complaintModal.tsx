import React from "react";
import "./complaintModal.css";

interface ComplaintModalProps {
  isOpen: boolean;
  content: string | null;
  onClose: () => void;
}

const ComplaintModal: React.FC<ComplaintModalProps> = ({
  isOpen,
  content,
  onClose,
}) => {
  if (!isOpen) return null;

  return (
    <div className="complaintModalOverlay" onClick={onClose}>
      <div
        className="complaintModalContainer"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="complaintModalTitle">Nội dung khiếu nại</h3>
        <p className="complaintModalContent">{content}</p>

        <button className="complaintModalCloseBtn" onClick={onClose}>
          Đóng
        </button>
      </div>
    </div>
  );
};

export default ComplaintModal;
