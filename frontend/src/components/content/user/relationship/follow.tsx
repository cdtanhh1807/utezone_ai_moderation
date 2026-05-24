import { useState } from "react";
import AccountService from "../../../../services/AccountService";
import type { FollowBlockRequest } from "../../../../services/AccountService";

interface FollowButtonProps {
  ownerEmail: string;
  clientEmail: string;
  onFollowSuccess?: () => void;
}

export const FollowButton = ({ ownerEmail, clientEmail, onFollowSuccess }: FollowButtonProps) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleFollow = async () => {
    setLoading(true);
    setMessage(null);

    const data: FollowBlockRequest = {
      owner: ownerEmail,
      client: clientEmail,
    };

    try {
      const res = await AccountService.follow(data);
      if (res.message) {
        setMessage("Follow thành công!");
        if (onFollowSuccess) onFollowSuccess(); // ⬅ cập nhật FE
      } else {
        setMessage("Follow thất bại!");
      }
    } catch (err) {
      console.error(err);
      setMessage("Có lỗi xảy ra. Vui lòng thử lại!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <button className="btn-follow" onClick={handleFollow} disabled={loading}>
      {loading ? "Đang xử lý..." : "Theo dõi"}
    </button>
  );
};
