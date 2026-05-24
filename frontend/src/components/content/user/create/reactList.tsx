import "./reactList.css";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import AccountService from "../../../../services/AccountService";
import type { UserInfo } from "../../../../types/Account";

// interface chung cho post/react comment
export interface Reacts {
  love: string[];
  like: string[];
  haha: string[];
  wow: string[];
  sad: string[];
  angry: string[];
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  reacts: Reacts; 
  userInfoMap: Record<string, UserInfo>; // email -> UserInfo
}

// Mapping react key sang tiếng Việt
const reactTypeVN: Record<string, string> = {
  love: "Yêu thích",
  like: "Thích",
  haha: "Haha",
  wow: "Wow",
  sad: "Buồn",
  angry: "Giận",
};

const getReactTabs = (reacts: Reacts) => {
  const entries = Object.entries(reacts);
  const filtered = entries.filter(([_, arr]) => arr.length > 0);
  const sorted = filtered.sort((a, b) => b[1].length - a[1].length);
  const top3 = sorted.slice(0, 3);
  const more = sorted.slice(3);
  return { all: sorted, top3, more };
};

const ReactList = ({ isOpen, onClose, reacts, userInfoMap }: Props) => {
  const { all, top3, more } = getReactTabs(reacts);

  const [activeTab, setActiveTab] = useState("all");

  // reset tab mỗi khi reacts thay đổi
  useEffect(() => {
    setActiveTab("all");
  }, [reacts]);

  // local state quản lý user info
  const [localUserInfoMap, setLocalUserInfoMap] = useState<Record<string, UserInfo>>(userInfoMap);

  // danh sách email cần fetch
  const emailsToFetch = Object.values(reacts).flat();

  useEffect(() => {
    if (!isOpen) return;

    emailsToFetch.forEach(email => {
      if (!localUserInfoMap[email]) {
        AccountService.get_account_info(email)
          .then(account => {
            if (account?.userInfo) {
              setLocalUserInfoMap(prev => ({ ...prev, [email]: account.userInfo }));
            }
          })
          .catch(err => console.error("Failed to fetch user info:", err));
      }
    });
  }, [isOpen, reacts]);

  const getUsersFromReactType = (type: string) => {
    if (type === "all") return all.flatMap(([_, users]) => users);
    if (type === "more") return more.flatMap(([_, users]) => users);
    return reacts[type as keyof Reacts] ?? [];
  };

  const users = getUsersFromReactType(activeTab);

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div 
          className="react-backdrop" 
          onClick={onClose}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="react-modal"
            onClick={(e) => e.stopPropagation()}
            initial={{ scale: 0.85, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.85, opacity: 0 }}
          >
            {/* Tabs */}
            <div className="react-tabs">
              <div
                className={`react-tab ${activeTab === "all" ? "active" : ""}`}
                onClick={() => setActiveTab("all")}
              >
                Tất cả
              </div>

              {top3.map(([type, arr]) => (
                <div
                  key={type}
                  className={`react-tab ${activeTab === type ? "active" : ""}`}
                  onClick={() => setActiveTab(type)}
                >
                  {reactTypeVN[type] || type} ({arr.length})
                </div>
              ))}

              {more.length > 0 && (
                <div
                  className={`react-tab ${activeTab === "more" ? "active" : ""}`}
                  onClick={() => setActiveTab("more")}
                >
                  Khác
                </div>
              )}
            </div>

            {/* User list */}
            <div className="react-list">
              {users.map((email) => {
                const u = localUserInfoMap[email];
                if (!u) return <div key={email}>Đang tải...</div>;

                return (
                  <div key={email} className="react-user">
                    <img src={u.avatar || ""} className="react-avatar" />
                    <span className="react-name">{u.fullName}</span>
                  </div>
                );
              })}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default ReactList;
