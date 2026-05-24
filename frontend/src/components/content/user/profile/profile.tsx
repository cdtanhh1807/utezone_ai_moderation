import "./profile.css";
import { useParams } from "react-router-dom";
import { useState, useRef, useEffect } from "react";
import ProfileHeader from "./profileHeader";
import logochat from "../../../../assets/logochat.png";
import ProfilePosts from "./profilePost";
import ProfileArchived from "./profileArchived";
import ProfileAlbum from "./profileAlbum";
import ProfileSaved from "./profileSaved";
import StoryBlock from "../create/storyBlock";
import ArticleOutlinedIcon from '@mui/icons-material/ArticleOutlined';
import ArticleIcon from '@mui/icons-material/Article';
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined';
import InventoryIcon from '@mui/icons-material/Inventory';
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import PhotoLibraryOutlinedIcon from '@mui/icons-material/PhotoLibraryOutlined';

import ChatDialog from "../chat/ChatDialog";
import useConversations from "../chat/useConversation";

function Profile() {
  const { email } = useParams<{ email: string }>();

  const [openMessage, setOpenMessage] = useState(false);
  const { list, refetch } = useConversations();
  const [activeTab, setActiveTab] = useState<"posts" |"album"| "archived" | "saved">(
    "posts",
  );

  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!openMessage) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) {
        setOpenMessage(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [openMessage]);

  return (
    <div className="my-profile">
      {/* ===== MAIN CONTENT ===== */}
      <div className="profile-main">
        <div className="header">
          <ProfileHeader email={email} />
        </div>

        <div className="storyBlock-profile">
          <StoryBlock />
        </div>

        {/* ===== TAB ===== */}
        <div className="profile-tabs">
            <button
              className={activeTab === "posts" ? "active" : ""}
              onClick={() => setActiveTab("posts")}
            >
              <ArticleOutlinedIcon />
            </button>

            <button
              className={activeTab === "album" ? "active" : ""}
              onClick={() => setActiveTab("album")}
            >
              <PhotoLibraryOutlinedIcon />
            </button>

          <button
            className={activeTab === "archived" ? "active" : ""}
            onClick={() => setActiveTab("archived")}
          >
            <Inventory2OutlinedIcon/>
          </button>

          <button
            className={activeTab === "saved" ? "active" : ""}
            onClick={() => setActiveTab("saved")}
          >
            <BookmarkBorderIcon/>
          </button>
        </div>

        {/* ===== CONTENT ===== */}
        <div className="p-post">
          {activeTab === "posts" && <ProfilePosts email={email} />}
          {activeTab === "album" && <ProfileAlbum/>}
          {activeTab === "archived" && <ProfileArchived />}
          {activeTab === "saved" && <ProfileSaved email={email} />}
        </div>
      </div>

      {/* ===== RIGHT SIDE ===== */}
      <div className="rightSide">
        <button
          className="floating-ribbon"
          onClick={() => setOpenMessage(true)}
        >
          <img src={logochat} alt="Chat" />
          <span className="chat-badge">5</span>
        </button>

        {/* ====== CHAT BOX ====== */}
        {openMessage && (
          <div ref={boxRef} className="chat-fixed">
            <ChatDialog onClose={() => setOpenMessage(false)} list={list} refetch={refetch} />
          </div>
        )}
      </div>
    </div>
  );
}

export default Profile;
