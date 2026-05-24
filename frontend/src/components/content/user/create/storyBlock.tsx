import React, { useEffect, useState, useRef } from "react";
import "../home/middleSide.css";
import type { Story } from "../../../../types/Story";
import AccountService from "../../../../services/AccountService";
import type { UserInfo } from "../../../../types/Account";
import { StoryService } from "../../../../services/StoryService";
import StoryModal from "../home/storyModal";
import CreateStory from "./createStory";
import { jwtDecode } from "jwt-decode";
import { ToastService } from "../../../../services/ToastService";
import { de } from "date-fns/locale";

const StoryBlock: React.FC = () => {
  const [userInfoMap, setUserInfoMap] = useState<Record<string, UserInfo>>({});
  const [isStoryModalOpen, setIsStoryModalOpen] = useState(false);
  const [storyStartUserId, setStoryStartUserId] = useState<string | null>(null);
  const [openCreateStory, setOpenCreateStory] = useState<boolean>(false);
  interface UserStory {
    userId: string;
    stories: Story[];
  }
  const [storys, setStorys] = useState<UserStory[]>([]);

  const token = localStorage.getItem("token");
  let currentUserEmail: string | null = null;

  if (token) {
    try {
      const decoded: any = jwtDecode(token);
      currentUserEmail = decoded.sub;
      console.log("per", decoded.per);
    } catch (err) {
      console.error("❌ Token không hợp lệ:", err);
    }
  }
  const canCreateContent = () => {
    const token = localStorage.getItem("token");
    if (!token) return false;

    try {
      const decoded: any = jwtDecode(token);
      const per = String(decoded.per || ""); // chắc chắn là chuỗi
      console.log("per check", per);
      return per[0] === "1"; // ký tự đầu tiên = '1' mới cho phép
    } catch {
      return false;
    }
  };

  const fetchStorys = async () => {
    try {
      const res = await StoryService.getTodayStories();
      console.log(res);
      setStorys(res.data);
    } catch (err) {
      console.error("❌ Lỗi fetch stories:", err);
    }
  };

  useEffect(() => {
    fetchStorys();
  }, []);

  useEffect(() => {
    if (!storys.length) return;

    const fetchAllUserInfoFromStories = async () => {
      const emailsSet = new Set<string>();
      storys.forEach((userStory) => {
        emailsSet.add(userStory.userId);

        userStory.stories.forEach((story) => {
          emailsSet.add(story.createdBy);
          story.viewedBy.forEach((email) => emailsSet.add(email));
        });
      });

      const emails = Array.from(emailsSet);

      const results = await Promise.all(
        emails.map(async (email) => {
          try {
            const res = await AccountService.get_account_info(email);
            return [email, res] as [string, UserInfo];
          } catch (err) {
            console.error("❌ Lỗi lấy user info:", email, err);
            return [email, null] as [string, UserInfo | null];
          }
        })
      );

      const userMap: Record<string, UserInfo> = {};
      results.forEach(([email, info]) => {
        if (info) userMap[email] = info;
      });

      setUserInfoMap(userMap);
    };

    fetchAllUserInfoFromStories();
  }, [storys]);

  return (
    <div className="storyBlock">
      <div
        className="storyPaticular"
        onClick={() => {
          if (!canCreateContent()) {
            ToastService.error("Tài khoản của bạn đã bị cấm đăng tải nội dung");
            return;
          }
          setOpenCreateStory(true);
        }}
      >
        <div className="imageDIv-add addStory">
          <span className="plusIcon">+</span>
        </div>
      </div>

      {/* STORY LIST */}
      {!storys || storys.length === 0 ? (
        <p></p>
      ) : (
        storys.map((u) => (
          <div className="storyPaticular" key={u.userId}>
            <div
              className="imageDIv"
              onClick={() => {
                setStoryStartUserId(u.userId);
                setIsStoryModalOpen(true);
              }}
            >
              <img
                className="statusImg"
                src={userInfoMap[u.userId]?.avatar || ""}
                alt={u.userId}
              />
            </div>
            <div className="profileName">
              @{userInfoMap[u.userId]?.fullName || u.userId}
            </div>
          </div>
        ))
      )}

      {isStoryModalOpen && storyStartUserId && (
        <StoryModal
          storys={storys}
          userInfoMap={userInfoMap}
          isOpen={isStoryModalOpen}
          onClose={() => setIsStoryModalOpen(false)}
          startUserId={storyStartUserId}
        />
      )}
      {openCreateStory && (
        <CreateStory
          isOpen={openCreateStory}
          onClose={() => setOpenCreateStory(false)}
          currentUser={currentUserEmail || ""}
        />
      )}
    </div>
  );
};

export default StoryBlock;
