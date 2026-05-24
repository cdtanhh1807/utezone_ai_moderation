import React from "react";
import "./department.css";
import { useNavigate } from "react-router-dom";

interface Department {
  email: string;
  fullName: string;
  avatar?: string;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  data: Department[];
}

const DepartmentModal: React.FC<Props> = ({ isOpen, onClose, data }) => {
  const navigate = useNavigate();

  if (!isOpen) return null;

  return (
    <div className="dept-modal-overlay" onClick={onClose}>
      <div className="dept-modal-content" onClick={(e) => e.stopPropagation()}>
        {/* HEADER */}
        <div className="dept-modal-header">
          <h2>Danh sách khoa</h2>
          <button className="dept-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        {/* BODY */}
        <div className="dept-modal-body">
          {data.length === 0 ? (
            <div className="dept-empty">Không có khoa nào</div>
          ) : (
            data.map((dept) => (
              <div
                key={dept.email}
                className="dept-item"
                onClick={() => {
                  onClose(); // 👈 tắt modal trước
                  navigate(`/profile/${dept.email}`);
                }}
              >
                <img
                  src={dept.avatar || "/default-avatar.png"}
                  className="dept-avatar"
                  alt=""
                />
                <div className="dept-info">
                  <div className="dept-name">{dept.fullName}</div>
                  <div className="dept-email">{dept.email}</div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default DepartmentModal;
