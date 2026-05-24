import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import AccountService from "../../../../services/AccountService";
import type { UserInfo, Account } from "../../../../types/Account";
import avt_default from "../../../../assets/avt_default.png";
import "./completeProfile.css";
import FileService from "../../../../services/FileService";

interface CompleteProfileProps {
  onDone?: () => void;
}

const CompleteProfile = ({ onDone }: CompleteProfileProps) => {
  const navigate = useNavigate();
  const [account, setAccount] = useState<Account | null>(null);

  const [formData, setFormData] = useState<Partial<UserInfo>>({});
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const [showSuggestModal, setShowSuggestModal] = useState(false);
  const [suggestUsers, setSuggestUsers] = useState<any[]>([]);

  useEffect(() => {
    const accData = localStorage.getItem("account");
    if (accData) {
      const parsed = JSON.parse(accData);
      setAccount(parsed);
    }
  }, []);

  useEffect(() => {
    if (account?.userInfo) {
      setFormData({
        fullName: account.userInfo.fullName || "",
        phone: account.userInfo.phone || "",
        address: account.userInfo.address || "",
        day_of_birth: account.userInfo.day_of_birth || "",
        description: account.userInfo.description || "",
        department: account.userInfo.department || "",
        avatar: account.userInfo.avatar || "",
      });
    }
  }, [account]);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFollow = async (email: string) => {
    try {
      await AccountService.follow({
        owner: account?.email!,
        client: email,
      });

      setSuggestUsers((prev) =>
        prev.map((u) =>
          u.email === email ? { ...u, followed: true } : u
        )
      );
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async () => {
    const requiredFields: (keyof UserInfo)[] = [
      "fullName",
      "phone",
      "address",
      "day_of_birth",
      "department",
      "description",
    ];

    for (let field of requiredFields) {
      if (!formData[field] || formData[field]?.toString().trim() === "") {
        setMsg(`Vui lòng nhập ${field.replace("_", " ")}!`);
        return;
      }
    }

    setLoading(true);
    setMsg(null);

    try {
      let avatarId = formData.avatar;

      if (!avatarId) {
        const response = await fetch(avt_default);
        const blob = await response.blob();

        const file = new File([blob], "default-avatar.jpg", {
          type: blob.type,
        });

        const uploadRes = await FileService.uploadPicture(file);
        avatarId = uploadRes.file_id;
      }

      const payload = {
        ...formData,
        avatar: avatarId,
      };

      await AccountService.updateProfile(payload);

      // ✅ gọi API đúng (không cần email)
      const suggestRes = await AccountService.get_suggest_follow({
        limit: 20,
      });

      // ✅ đúng field
      setSuggestUsers(suggestRes.suggestions || []);
      setShowSuggestModal(true);

      setMsg("Cập nhật hồ sơ thành công!");
      if (onDone) onDone();
    } catch (err) {
      console.error(err);
      setMsg("Có lỗi xảy ra. Vui lòng thử lại!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="cp-container">
      <h2 className="cp-title">Hoàn thiện thông tin cá nhân</h2>

      <div className="cp-form">
        <label>Họ và tên *</label>
        <input
          name="fullName"
          value={formData.fullName || ""}
          onChange={handleChange}
        />

        <label>Số điện thoại *</label>
        <input
          name="phone"
          value={formData.phone || ""}
          onChange={handleChange}
        />

        <label>Địa chỉ *</label>
        <input
          name="address"
          value={formData.address || ""}
          onChange={handleChange}
        />

        <label>Ngày sinh *</label>
        <input
          type="date"
          name="day_of_birth"
          value={formData.day_of_birth || ""}
          onChange={handleChange}
        />

        <label>Phòng ban *</label>
        <select
          name="department"
          value={formData.department || ""}
          onChange={handleChange}
        >
          <option value="">-- Chọn phòng ban --</option>
          <option value="CÔNG NGHỆ THÔNG TIN">CÔNG NGHỆ THÔNG TIN</option>
          <option value="ĐIỆN - ĐIỆN TỬ">ĐIỆN - ĐIỆN TỬ</option>
          <option value="CƠ KHÍ CHẾ TẠO MÁY">CƠ KHÍ CHẾ TẠO MÁY</option>
          <option value="KINH TẾ">KINH TẾ</option>
        </select>

        <label>Giới thiệu bản thân *</label>
        <textarea
          name="description"
          value={formData.description || ""}
          onChange={handleChange}
        />
      </div>

      {msg && <p className="cp-message">{msg}</p>}

      <button className="cp-btn" onClick={handleSubmit} disabled={loading}>
        {loading ? "Đang lưu..." : "Lưu thông tin"}
      </button>

      {/* MODAL */}
      {showSuggestModal && (
        <div className="modal-suggest-overlay">
          <div className="modal-suggest">
            <h3>Gợi ý kết bạn</h3>

            <div className="suggest-list">
              {suggestUsers.map((user) => (
                <div key={user.email} className="suggest-item">
                  <img src={user.avatar} alt="" />
                  <span>{user.fullName}</span>

                  <button
                    onClick={() => handleFollow(user.email)}
                    disabled={user.followed}
                  >
                    {user.followed ? "Đã follow" : "Follow"}
                  </button>
                </div>
              ))}
            </div>

            <button
              onClick={() => {
                setShowSuggestModal(false);
                navigate("/home");
              }}
            >
              Bỏ qua
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CompleteProfile;