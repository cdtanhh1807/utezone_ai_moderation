import React, { useEffect, useState } from "react";
import type { Conversation } from "./useConversation";
import "./ConversationList.css";
import accountAPI from "../../../../services/AccountService";
import AddIcon from "@mui/icons-material/Add";

type Props = {
  list: Conversation[];
  selected: string | null;
  onSelect: (email: string) => void;
};

const ConversationList: React.FC<Props> = ({ list, selected, onSelect }) => {
  // Map lưu thông tin user: key = email, value = { fullName, avatar }
  const [userInfoMap, setUserInfoMap] = useState<
    Record<string, { fullName: string; avatar: string }>
  >({});

  useEffect(() => {
    list.forEach(async (c) => {
      if (!userInfoMap[c.other_email]) {
        try {
          const data = await accountAPI.get_account_info(c.other_email);
          setUserInfoMap((prev) => ({
            ...prev,
            [c.other_email]: { fullName: data.fullName, avatar: data.avatar },
          }));
        } catch (err) {
          console.error("Lỗi lấy thông tin user:", err);
        }
      }
    });
  }, [list]); // chạy khi list thay đổi

  const goToProfile = (email: string) => {
    window.location.href = `/profile/${email}`;
  };

  return (
    <div className="conv-list-container">
      <div className="message_header">
        Tin nhắn
        <button className="btn-add-mesage">
          <AddIcon />
        </button>
      </div>
      {list.map((c) => {
        const isActive = c.other_email === selected;
        const userInfo = userInfoMap[c.other_email];

        return (
          <div
            key={c.other_email}
            onClick={() => onSelect(c.other_email)}
            className={`conv-item ${isActive ? "active" : ""} ${
              c.has_new ? "new-msg" : ""
            }`}
          >
            <div className="conv-row">
              {userInfo?.avatar && (
                <img
                  className="postInfoImg"
                  src={userInfo.avatar}
                  alt="avatar"
                  style={{ cursor: "pointer" }}
                  onClick={(e) => {
                    e.stopPropagation(); // tránh trigger onSelect
                    goToProfile(c.other_email);
                  }}
                />
              )}
              <span className="conv-name" style={{ cursor: "pointer" }}>
                {userInfo?.fullName || c.full_name}{" "}
              </span>
              {c.has_new && <span className="conv-dot" />}
            </div>
            {!isActive && <div className="conv-last-msg">{c.last_message}</div>}
          </div>
        );
      })}
    </div>
  );
};

export default ConversationList;
