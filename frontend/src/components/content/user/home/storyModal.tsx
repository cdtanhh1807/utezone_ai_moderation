import React, { useState, useEffect, useRef } from "react";
import type { Story } from "../../../../types/Story";
import type { UserInfo } from "../../../../types/Account";
import PauseIcon from "@mui/icons-material/Pause";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";
import VolumeOffIcon from "@mui/icons-material/VolumeOff";
import { useNavigate } from "react-router-dom";
import "./storyModal.css";
import { ToastService } from "../../../../services/ToastService";
import ChevronLeftOutlinedIcon from "@mui/icons-material/ChevronLeftOutlined";
import ChevronRightOutlinedIcon from "@mui/icons-material/ChevronRightOutlined";
import { jwtDecode } from "jwt-decode";
import { StoryService } from "../../../../services/StoryService";

interface UserStory {
  userId: string;
  stories: Story[];
}

interface StoryModalProps {
  storys: UserStory[];
  userInfoMap: Record<string, UserInfo>;
  isOpen: boolean;
  onClose: () => void;
  startUserId: string;
}

const StoryModal: React.FC<StoryModalProps> = ({
  storys,
  userInfoMap,
  isOpen,
  onClose,
  startUserId,
}) => {
  const [localStorys, setLocalStorys] = useState<UserStory[]>(storys);
  const [currentUserIndex, setCurrentUserIndex] = useState(0);
  const [currentStoryIndex, setCurrentStoryIndex] = useState(0);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const musicRef = useRef<HTMLAudioElement | null>(null);

  const [isPlaying, setIsPlaying] = useState(true);
  const [volume, setVolume] = useState(1);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const navigate = useNavigate();

  // decode token để lấy currentUserEmail
  const token = localStorage.getItem("token");
  let currentUserEmail: string | null = null;
  if (token) {
    try {
      interface JwtPayload {
        sub: string;
        exp: number;
      }
      const decoded: JwtPayload = jwtDecode<JwtPayload>(token);
      currentUserEmail = decoded.sub;
    } catch (err) {
      console.error("❌ Token không hợp lệ:", err);
    }
  }

  // sync state localStorys khi props thay đổi
  useEffect(() => {
    setLocalStorys(storys);
    const startIndex = storys.findIndex((u) => u.userId === startUserId);
    setCurrentUserIndex(startIndex >= 0 ? startIndex : 0);
    setCurrentStoryIndex(0);
  }, [storys, startUserId]);

  if (!isOpen || localStorys.length === 0) return null;

  const currentUserStory = localStorys[currentUserIndex];
  const currentStory = currentUserStory.stories[currentStoryIndex];
  const userInfo = userInfoMap[currentUserStory.userId];

  const mediaSrc =
    currentStory.mediaUrls?.[0] || currentStory.thumbnails?.[0] || "";

  // ------------------- LOAD VIDEO -------------------
  useEffect(() => {
    const vid = videoRef.current;
    if (!vid) return;

    vid.pause();

    if (currentStory.mediaType === "video") {
      vid.src = mediaSrc;
      vid.muted = currentStory.videoTrim?.hasOriginalSound === false;
      const trim = currentStory.videoTrim;

      vid.onloadedmetadata = () => {
        const start = trim?.startAt ?? 0;
        vid.currentTime = start;

        vid
          .play()
          .then(() => setIsPlaying(true))
          .catch(() => setIsPlaying(false));

        if (trim?.duration) {
          const end = start + trim.duration;

          const check = () => {
            if (vid.currentTime >= end) {
              vid.currentTime = start; // LOOP
              vid.play();
            }
          };
          vid.addEventListener("timeupdate", check);
          return () => vid.removeEventListener("timeupdate", check);
        }
      };
    }

    return () => vid.pause();
  }, [currentUserIndex, currentStoryIndex, currentStory.mediaUrls]);

  // ------------------- LOAD MUSIC -------------------
  useEffect(() => {
    const audio = musicRef.current;
    if (!audio) return;

    audio.pause();
    const music = currentStory.music;
    if (!music || !music.fileid) return;

    audio.src = music.url || music.fileid;

    audio.onloadedmetadata = () => {
      const start = music.startAt ?? 0;
      audio.currentTime = start;
      audio.play().catch(() => {});

      if (music.duration) {
        const end = start + music.duration;
        const check = () => {
          if (audio.currentTime >= end) {
            audio.currentTime = start;
            audio.play();
          }
        };
        audio.addEventListener("timeupdate", check);
        return () => audio.removeEventListener("timeupdate", check);
      }
    };

    return () => audio.pause();
  }, [currentUserIndex, currentStoryIndex, currentStory.music?.fileid]);

  // ------------------- VOLUME -------------------
  useEffect(() => {
    if (videoRef.current) videoRef.current.volume = volume;
    if (musicRef.current) musicRef.current.volume = volume;
  }, [volume]);

  // ------------------- CONTROLS -------------------
  const togglePlay = () => {
    const vid = videoRef.current;
    const audio = musicRef.current;

    if (isPlaying) {
      vid?.pause();
      audio?.pause();
      setIsPlaying(false);
    } else {
      vid?.play();
      audio?.play();
      setIsPlaying(true);
    }
  };

  const toggleVolume = () => {
    setVolume(volume === 0 ? 1 : 0);
  };

  const handleNext = () => {
    if (currentStoryIndex < currentUserStory.stories.length - 1) {
      setCurrentStoryIndex(currentStoryIndex + 1);
    } else {
      const nextUserIndex = (currentUserIndex + 1) % localStorys.length;
      setCurrentUserIndex(nextUserIndex);
      setCurrentStoryIndex(0);
    }
  };

  const handlePrev = () => {
    if (currentStoryIndex > 0) {
      setCurrentStoryIndex(currentStoryIndex - 1);
    } else {
      const prevUserIndex =
        (currentUserIndex - 1 + localStorys.length) % localStorys.length;
      setCurrentUserIndex(prevUserIndex);
      setCurrentStoryIndex(localStorys[prevUserIndex].stories.length - 1);
    }
  };

  // ------------------- DELETE STORY -------------------
  const handleDeleteStory = async (storyId: string) => {
    ToastService.confirm("Bạn có chắc muốn xóa tin này?", async () => {
      try {
        await StoryService.deleteStory(storyId);
        ToastService.success("Đã xóa tin");

        // Reload sau 0.5s để toast hiển thị
        setTimeout(() => {
          window.location.reload();
        }, 500);

        setLocalStorys((prev) => {
          const updated = prev
            .map((userStory) => ({
              ...userStory,
              stories: userStory.stories.filter((s) => s._id !== storyId),
            }))
            .filter((userStory) => userStory.stories.length > 0);

          if (updated.length === 0) {
            onClose(); // hết story → đóng modal
            return [];
          }

          if (currentStoryIndex >= updated[currentUserIndex]?.stories.length) {
            setCurrentStoryIndex(
              Math.max(0, updated[currentUserIndex]?.stories.length - 1)
            );
          }

          return updated;
        });
      } catch (error: any) {
        console.error("Lỗi xóa story:", error);
        ToastService.error(error.response?.data?.detail || "Xóa tin thất bại");
      }
    });

    setIsMenuOpen(false);
  };

  const handleReportStory = () => {
    alert("Báo cáo story!");
    setIsMenuOpen(false);
  };

  return (
    <div className="storyModalOverlay">
      <button className="closeBtn" onClick={onClose}>
        ✖
      </button>
      <div className="storyModalContent">
        <div className="storyHeader">
          <img
            className="avatar"
            onClick={() => navigate(`/profile/${currentStory.createdBy || ""}`)}
            style={{ cursor: "pointer" }}
            src={userInfo?.avatar || ""}
          />
          <span
            className="username"
            onClick={() => navigate(`/profile/${currentStory.createdBy || ""}`)}
            style={{ cursor: "pointer" }}
          >
            {userInfo?.fullName}
          </span>

          <div className="musicControls">
            <button className="str-pause-btn" onClick={togglePlay}>
              {isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
            </button>

            <button onClick={toggleVolume}>
              {volume === 0 ? <VolumeOffIcon /> : <VolumeUpIcon />}
            </button>
            <div
              className="storyMenuWrapper"
              style={{ position: "relative", display: "inline-block" }}
            >
              <button
                className="storyMenuBtn"
                onClick={() => setIsMenuOpen((prev) => !prev)}
              >
                ⋮
              </button>
              {isMenuOpen && (
                <div className="storyMenuDropdown">
                  {currentUserEmail === currentUserStory.userId ? (
                    <button onClick={() => handleDeleteStory(currentStory._id)}>
                      Xóa
                    </button>
                  ) : (
                    <button onClick={handleReportStory}>Báo cáo</button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="storyMedia">
          {currentStory.mediaType === "image" ? (
            <img src={mediaSrc} alt="" />
          ) : (
            <video ref={videoRef} />
          )}

          {currentStory.textLayers?.map((layer, idx) => (
            <div
              key={idx}
              style={{
                position: "absolute",
                left: `${layer.x}%`,
                top: `${layer.y}%`,
                transform: `translate(-50%, -50%) scale(${
                  layer.scale ?? 1
                }) rotate(${layer.rotate ?? 0}deg)`,
                color: layer.color,
                fontFamily: layer.font || "Arial",
                fontSize: layer.fontSize,
                backgroundColor: layer.background || "transparent",
                whiteSpace: "pre-wrap",
              }}
            >
              {layer.text}
            </div>
          ))}
        </div>

        <div className="storyControls">
          <ChevronLeftOutlinedIcon
            className="s-nav-left"
            onClick={handlePrev}
          />
          <ChevronRightOutlinedIcon
            className="s-nav-right"
            onClick={handleNext}
          />
        </div>

        <audio ref={musicRef} hidden />
      </div>
    </div>
  );
};

export default StoryModal;
