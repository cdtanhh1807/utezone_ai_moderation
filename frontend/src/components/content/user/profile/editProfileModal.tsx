import "./editProfileModal.css";
import { useState, useRef } from "react";
import AccountService from "../../../../services/AccountService";
import FileService from "../../../../services/FileService";
import type { UserInfo } from "../../../../types/Account";
import { ToastService } from "../../../../services/ToastService";

interface ModalProps {
  user: UserInfo;
  onClose: () => void;
}

const EditProfileModal = ({ user, onClose }: ModalProps) => {
  const [description, setDescription] = useState(user.description || "");
  const [avatar, setAvatar] = useState(user.avatar || "");
  const [preview, setPreview] = useState(user.avatar || "");

  const [fullName, setFullName] = useState(user.fullName || "");
  const [phone, setPhone] = useState(user.phone || "");
  const [address, setAddress] = useState(user.address || "");
  const [dayOfBirth, setDayOfBirth] = useState(user.day_of_birth || "");
  const [department, setDepartment] = useState(user.department || "");

  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleClickUpload = () => {
    fileInputRef.current?.click();
  };

  const handleUploadAvatar = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const res = await FileService.uploadPicture(file);
      setAvatar(res.file_id);
      setPreview(res.url);
    } catch (err) {
      console.error(err);
      ToastService.error("Tải ảnh đại diện thất bại!");
    }
  };

  const handleSave = async () => {
    try {
      const updateData: any = {};

      if (avatar !== user.avatar) updateData.avatar = avatar;
      if (description !== (user.description || "")) updateData.description = description;
      if (fullName !== (user.fullName || "")) updateData.fullName = fullName;
      if (phone !== (user.phone || "")) updateData.phone = phone;
      if (address !== (user.address || "")) updateData.address = address;
      if (dayOfBirth !== (user.day_of_birth || "")) updateData.day_of_birth = dayOfBirth;
      if (department !== (user.department || "")) updateData.department = department;

      if (Object.keys(updateData).length === 0) {
        ToastService.info("Không có thay đổi nào để cập nhật.");
        return;
      }

      await AccountService.updateProfile(updateData);
      setToast({ message: "Cập nhật thành công!", type: "success" });
      onClose();
      window.location.reload();
    } catch (err) {
      console.error(err);
      setToast({ message: "Cập nhật thất bại!", type: "error" });
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-container">
        <h2>Thông Tin Cá Nhân</h2>

        {/* Avatar */}
        <div className="field">
          <label className="edit-title">Ảnh đại diện</label>
          <div className="edit-postInfo">
            <img className="edit-postInfoImg" src={preview} alt="avatar" />
            <button className="btn-change-avatar" onClick={handleClickUpload}>
              Thay đổi ảnh đại diện
            </button>
            <input
              type="file"
              accept="image/*"
              ref={fileInputRef}
              style={{ display: "none" }}
              onChange={handleUploadAvatar}
            />
          </div>
        </div>

        {/* FULL NAME */}
        <div className="field">
          <label className="edit-title">Tên</label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Nhập họ tên..."
          />
        </div>

        {/* PHONE */}
        <div className="field">
          <label className="edit-title">Số điện thoại</label>
          <input
            type="text"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="Số điện thoại..."
          />
        </div>

        {/* ADDRESS */}
        <div className="field">
          <label className="edit-title">Địa chỉ</label>
          <input
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="Địa chỉ..."
          />
        </div>

        {/* DATE OF BIRTH */}
        <div className="field">
          <label className="edit-title">Ngày sinh</label>
          <input
            type="date"
            value={dayOfBirth}
            onChange={(e) => setDayOfBirth(e.target.value)}
          />
        </div>

        {/* DEPARTMENT */}
        {/* DEPARTMENT */}
        <div className="field">
          <label className="edit-title">Thuộc Phòng/Khoa</label>
          <select
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
          >
            <option value="">Chọn khoa/phòng ban</option>
            <option value="CHÍNH TRỊ LUẬT">CHÍNH TRỊ LUẬT</option>
            <option value="CƠ KHÍ CHẾ TẠO MÁY">CƠ KHÍ CHẾ TẠO MÁY</option>
            <option value="CƠ KHÍ ĐỘNG LỰC">CƠ KHÍ ĐỘNG LỰC</option>
            <option value="CÔNG NGHỆ HÓA HỌC VÀ THỰC PHẨM">CÔNG NGHỆ HÓA HỌC VÀ THỰC PHẨM</option>
            <option value="CÔNG NGHỆ THÔNG TIN">CÔNG NGHỆ THÔNG TIN</option>
            <option value="ĐIỆN - ĐIỆN TỬ">ĐIỆN - ĐIỆN TỬ</option>
            <option value="IN VÀ TRUYỀN THÔNG">IN VÀ TRUYỀN THÔNG</option>
            <option value="KHOA HỌC ỨNG DỤNG">KHOA HỌC ỨNG DỤNG</option>
            <option value="KINH TẾ">KINH TẾ</option>
            <option value="NGOẠI NGỮ">NGOẠI NGỮ</option>
            <option value="THỜI TRANG VÀ DU LỊCH">THỜI TRANG VÀ DU LỊCH</option>
            <option value="XÂY DỰNG">XÂY DỰNG</option>
            <option value="VIỆN SƯ PHẠM KỸ THUẬT">VIỆN SƯ PHẠM KỸ THUẬT</option>
          </select>
        </div>


        {/* DESCRIPTION */}
        <div className="field">
          <label className="edit-title">Description</label>
          <textarea
            rows={3}
            value={description}
            onChange={(e) => {
              const words = e.target.value.split(/\s+/);
              if (words.length <= 100) setDescription(e.target.value);
              else setDescription(words.slice(0, 100).join(" "));
            }}
            placeholder="Viết vài dòng mô tả..."
          />
          <small>{description.split(/\s+/).filter(Boolean).length} / 100</small>
        </div>

        {/* Buttons */}
        <div className="modal-actions">
          <button onClick={onClose} className="btn-cancel">Cancel</button>
          <button onClick={handleSave} className="btn-save">Save</button>
        </div>
      </div>
    </div>
  );
};

export default EditProfileModal;
