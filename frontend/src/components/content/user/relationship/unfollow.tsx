import { useState } from "react";
import AccountService from "../../../../services/AccountService";
import type { FollowBlockRequest } from "../../../../services/AccountService";

interface UnFollowButtonProps {
  ownerEmail: string;
  clientEmail: string;
  onUnFollowSuccess?: () => void;
}

export const UnFollowButton = ({ ownerEmail, clientEmail, onUnFollowSuccess }: UnFollowButtonProps) => {
  const [loading, setLoading] = useState(false);

  const handleUnFollow = async () => {
    setLoading(true);

    const data: FollowBlockRequest = { owner: ownerEmail, client: clientEmail };

    try {
      const res = await AccountService.un_follow(data);
      if (res.message && onUnFollowSuccess) onUnFollowSuccess();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button className="btn-message" onClick={handleUnFollow} disabled={loading}>
      {loading ? "Đang xử lý..." : "Bỏ theo dõi"}
    </button>
  );
};
