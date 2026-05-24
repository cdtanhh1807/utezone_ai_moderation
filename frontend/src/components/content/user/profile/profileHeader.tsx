import "./profileHeader.css";
import { useRef, useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";
import AccountService from "../../../../services/AccountService";
import type { UserInfo } from "../../../../types/Account";
import EditProfileModal from "./editProfileModal";
import { FollowButton } from "../relationship/follow";
import { UnFollowButton } from "../relationship/unfollow";
import type { Post } from "../../../../types/Post";
import { postAPI } from "../../../../services/PostService";
import EditIcon from "@mui/icons-material/Edit";
import { messageAPI } from "../chat/messageService";
import ChatDialog from "../chat/ChatDialog";
import useConversations from "../chat/useConversation";
import MoreHorizIcon from "@mui/icons-material/MoreHoriz";
import ReportModal from "../report/reportModal";
import { useNavigate } from "react-router-dom";
import { ToastService } from "../../../../services/ToastService";

interface ProfileHeaderProps {
  email?: string;
}

const ProfileHeader: React.FC<ProfileHeaderProps> = ({ email }) => {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [posts, setPosts] = useState<Post[]>([]);
  const [openMessage, setOpenMessage] = useState(false);
  const boxRef = useRef<HTMLDivElement>(null);
  const [openMenu, setOpenMenu] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const [openReportModal, setOpenReportModal] = useState(false);
  const [reportEmail, setReportEmail] = useState<string | null>(null);
  const navigate = useNavigate();
  const { list, refetch } = useConversations();

  let token = localStorage.getItem("token");
  interface JwtPayload {
    sub: string;
    exp: number;
  }
  let decodedEmail: string | null = null;

  if (token) {
    try {
      const decoded: JwtPayload = jwtDecode<JwtPayload>(token);
      decodedEmail = decoded.sub;
    } catch (err) {
      console.error("❌ Token không hợp lệ:", err);
    }
  }
  const currentUserEmail: string | null = email || decodedEmail;

  console.log(
    "Current User Email in ProfileHeader:",
    decodedEmail,
    currentUserEmail
  );

  useEffect(() => {
    if (!openMessage) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) {
        setOpenMessage(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [openMessage]);
  useEffect(() => {
    const fetchUser = async () => {
      if (!currentUserEmail) {
        console.error("❌ Không có email để fetch thông tin người dùng");
        setLoading(false);
        return;
      }

      try {
        const res = await AccountService.get_account_info(currentUserEmail);
        setUser(res || null);
        let ress;
        ress = await postAPI.getByEmail(currentUserEmail);
        setPosts(ress.post_list || []);
      } catch (err) {
        console.error("❌ Lỗi gọi API account_info:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [currentUserEmail]);
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpenMenu(false);
      }
    };

    if (openMenu) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [openMenu]);

  if (loading) return <div>Đang tải...</div>;
  if (!user) return <div>Không tìm thấy thông tin người dùng.</div>;

  const followersCount = user?.followers?.length || 0;
  const followingCount = user?.followed?.length || 0;
  const postsCount = posts?.length || 0;

  const isCurrentUser = decodedEmail === currentUserEmail;

  const hasFollowed = user?.followers?.includes(decodedEmail || "") || false;

  const handleSendMessage = async () => {
    if (!currentUserEmail) return;

    try {
      await messageAPI.send(email!, { content: "Bắt đầu trò chuyện!" });
      console.log("Đã gửi tin nhắn hello");
    } catch (err) {
      console.error("Lỗi gửi tin nhắn:", err);
    }
  };

  const checkConversationExists = async (): Promise<boolean> => {
    if (!decodedEmail || !currentUserEmail) return false;

    try {
      const res = await messageAPI.getConversation(currentUserEmail);
      const messages = res.data || [];

      const myConversationId1 = `${decodedEmail}_${currentUserEmail}`;
      const myConversationId2 = `${currentUserEmail}_${decodedEmail}`;

      return messages.some(
        (m: any) =>
          m.conversation_id === myConversationId1 ||
          m.conversation_id === myConversationId2
      );
    } catch (err) {
      console.error("❌ Lỗi kiểm tra conversation:", err);
      return false;
    }
  };

  return (
    <>
      <div className="profileHeader">
        <div className="header-imageDIv">
          {user.avatar && (
            <img className="profile-avatar" src={user.avatar} alt="avatar" />
          )}
        </div>

        <div className="profile-info">
          <div className="profile-username-time">
            <span className="profile-username">{user.fullName}</span>

            {isCurrentUser ? (
              <button
                className="btn-edit-profile"
                onClick={() => setIsModalOpen(true)}
              >
                <EditIcon sx={{ fontSize: 15 }} />
              </button>
            ) : (
              <>
                {hasFollowed ? (
                  <UnFollowButton
                    ownerEmail={decodedEmail || ""}
                    clientEmail={currentUserEmail || ""}
                    onUnFollowSuccess={() => {
                      setUser((prev) =>
                        prev
                          ? {
                              ...prev,
                              followers: (prev.followers ?? []).filter(
                                (f) => f !== decodedEmail
                              ),
                            }
                          : prev
                      );
                    }}
                  />
                ) : (
                  <FollowButton
                    ownerEmail={decodedEmail || ""}
                    clientEmail={currentUserEmail || ""}
                    onFollowSuccess={() => {
                      setUser((prev) =>
                        prev
                          ? {
                              ...prev,
                              followers: [
                                ...(prev.followers ?? []),
                                decodedEmail || "",
                              ],
                            }
                          : prev
                      );
                    }}
                  />
                )}
                <button
                  className="btn-message"
                  onClick={async () => {
                    const exists = await checkConversationExists();

                    if (!exists) {
                      await handleSendMessage();
                    }

                    setOpenMessage(true);
                  }}
                >
                  Nhắn tin
                </button>
                <div style={{ position: "relative" }}>
                  <button
                    className="dot-btn-message"
                    onClick={(e) => {
                      e.stopPropagation();
                      setOpenMenu((prev) => !prev);
                    }}
                  >
                    <MoreHorizIcon />
                  </button>

                  {openMenu && (
                    <div ref={menuRef} className="account-menu">
                      <div
                        className="menu-item"
                        onClick={() => {
                          setOpenMenu(false);
                          setReportEmail(currentUserEmail); // email tài khoản bị báo cáo
                          setOpenReportModal(true);
                        }}
                      >
                        🚩 Báo cáo tài khoản
                      </div>

                      <div
                        className="menu-item danger"
                        onClick={() => {
                          setOpenMenu(false);

                          ToastService.confirm(
                            "Bạn chắc chắn muốn chặn tài khoản này?",
                            async () => {
                              try {
                                await AccountService.block({
                                  owner: decodedEmail!,
                                  client: currentUserEmail!,
                                });

                                ToastService.success("Chặn thành công");

                                navigate("/home");
                              } catch (error) {
                                console.error("❌ Lỗi chặn tài khoản:", error);
                                ToastService.error("Chặn thất bại");
                              }
                            },
                            {
                              confirmText: "Chặn",
                              cancelText: "Hủy",
                            }
                          );
                        }}
                      >
                        ⛔ Chặn tài khoản
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>

          <div className="profile-overview">
            <div className="number">
              <span className="count">{postsCount}</span>
              <span className="label">Bài viết</span>
            </div>
            <div className="number">
              <span className="count">{followersCount}</span>
              <span className="label">Người theo dõi</span>
            </div>
            <div className="number">
              <span className="count">{followingCount}</span>
              <span className="label">Đang theo dõi</span>
            </div>
          </div>

          <div className="profile-description">
            <span className="full-name">KHOA {user.department || ""}</span>
            <span className="bio">
              {user.description || "Chưa cập nhật bio"}
            </span>
          </div>
        </div>
        <div></div>
      </div>

      {isModalOpen && (
        <EditProfileModal user={user} onClose={() => setIsModalOpen(false)} />
      )}
      {openMessage && (
        <div ref={boxRef} className="chat-fixed">
          <ChatDialog onClose={() => setOpenMessage(false)} list={list} refetch={refetch} />
        </div>
      )}
      {openReportModal && reportEmail && (
        <ReportModal
          isOpen={openReportModal}
          onClose={() => {
            setOpenReportModal(false);
            setReportEmail(null);
          }}
          policy_type="tài khoản"
          type="account"
          violatorEmail={reportEmail}
          content="" // báo cáo tài khoản không cần content
        />
      )}
    </>
  );
};

export default ProfileHeader;
