import React, { useState, useEffect } from "react";
import "./approveModal.css";
import { reportAPI } from "../../../../services/ReportService";
import CloseIcon from "@mui/icons-material/Close";
import type { Post } from "../../../../types/Post";
import type { Comment } from "../../../../types/Post";
import { ToastService } from "../../../../services/ToastService";

interface Policy {
  _id: string;
  name: string;
  description: string;
}

interface ApproveModalProps {
  isOpen: boolean;
  onClose: () => void;
  policy_element: string;
  element: string;
  elementId: string;
  elementParentId?: string | null;
  currentUserEmail: string; 
  post?: Post;
  comment?: Comment;
  onRemoved?: () => void;
}

const ApproveModal: React.FC<ApproveModalProps> = ({
  isOpen,
  onClose,
  policy_element,
  element,
  elementId,
  elementParentId,
  currentUserEmail,
  post,
  comment,
  onRemoved
}) => {
  const [policy, setPolicy] = useState<Policy | null>(null);
  const [loading, setLoading] = useState(false);

  // Lấy policy từ backend
  useEffect(() => {
    if (isOpen) {
      reportAPI.getAllAnnounce(policy_element).then((data) => {
        if (data.policy_list && data.policy_list.length > 0) {
          const p = data.policy_list[0]; // backend trả về 1 policy
          setPolicy({
            _id: p._id,
            name: p.name,
            description: p.description,
          });
        }
      });
    }
  }, [isOpen, element]);

  const handleRemove = async () => {
    if (!policy) return;
    setLoading(true);

    try {
      const isPost = element === "post";
      const isComment = element === "comment";

      const violatorEmail = isPost ? post?.createdBy : comment?.commentBy;

      const content = isPost ? post?.content : comment?.content;

      const contentId = isPost ? post?._id : comment?.commentId;

      if (!violatorEmail || !contentId) {
        ToastService.error("Dữ liệu không hợp lệ");
        return;
      }

      /* =========================
       * 2️⃣ PAYLOAD GỬI REPORT
       * ========================= */
      const reportPayload = {
        violatorEmail,
        annunciatorEmail: currentUserEmail,
        policyId: policy._id,
        typeContent: element, // post | comment
        contentId: contentId,
        contentParentId: elementParentId,
        // elementParentId: elementParentId,
        content: content || "",
        description: "",
        check: false,
      };

      /* =========================
       * 3️⃣ PAYLOAD APPROVE
       * ========================= */
      const approvePayload = {
        element,
        elementId: contentId,
        elementParentId: isComment ? elementParentId : null,
        policyId: policy._id,
        approveBy: currentUserEmail,
        action: "remove",
      };

      /* =========================
       * 4️⃣ CALL API
       * ========================= */
      await reportAPI.sendReport(reportPayload);
      await reportAPI.approveReport(approvePayload);

      ToastService.success(
        isPost ? "Bài viết đã được gỡ." : "Bình luận đã được gỡ."
      );
      onRemoved?.();
      onClose();
    } catch (error) {
      console.error("Approve error:", error);
      ToastService.error("Đã xảy ra lỗi, vui lòng thử lại.");
    } finally {
      setLoading(false);
    }
  };

  return (
    isOpen && (
      <div className="approveModalContainer">
        <div className="approveModal" onClick={(e) => e.stopPropagation()}>
          <div className="modalHeader">
            <h2>
              {element === "post"
                ? "Gỡ bài đăng vi phạm"
                : element === "comment"
                ? "Gỡ bình luận vi phạm"
                : "Gỡ nội dung vi phạm"}
            </h2>
            <CloseIcon className="closeIcon" onClick={onClose} />
          </div>

          <div className="modalContent">
            {policy ? (
              <>
                <p>
                  Bạn muốn gỡ bài viết vi phạm chính sách: <b>{policy.name}</b>
                </p>
                <p>{policy.description}</p>
              </>
            ) : (
              <p>Đang tải thông tin chính sách...</p>
            )}
          </div>

          <div className="modalFooter">
            <button className="cancelBtn" onClick={onClose}>
              Hủy
            </button>
            <button
              className="submitBtn"
              onClick={handleRemove}
              disabled={loading || !policy}
            >
              {loading
                ? "Đang xử lý..."
                : element === "post"
                ? "Gỡ bài đăng"
                : element === "comment"
                ? "Gỡ bình luận"
                : "Gỡ nội dung"}
            </button>
          </div>
        </div>
      </div>
    )
  );
};

export default ApproveModal;
