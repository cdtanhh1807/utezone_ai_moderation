import React, { useEffect, useRef, useState, useLayoutEffect } from "react";
import useChat from "./useChat";
import { useAuth } from "./AuthContext";
import accountAPI from "../../../../services/AccountService";
import FileService from "../../../../services/FileService";
import "./MessagePanel.css";
import SendRoundedIcon from "@mui/icons-material/SendRounded";
import ImageOutlinedIcon from "@mui/icons-material/ImageOutlined";
import AttachFileOutlinedIcon from "@mui/icons-material/AttachFileOutlined";

type Props = {
  otherEmail: string;
};

type PreviewItem = {
  file: File;
  url: string;
};

const FILE_BASE_URL = "http://localhost:8000/file";

const MessagePanel: React.FC<Props> = ({ otherEmail }) => {
  const { email: me } = useAuth();
  const { messages, sendMessage } = useChat(otherEmail);

  const [images, setImages] = useState<PreviewItem[]>([]);
  const [files, setFiles] = useState<PreviewItem[]>([]);
  const [text, setText] = useState("");

  const [userInfo, setUserInfo] = useState<{
    fullName: string;
    avatar: string;
  } | null>(null);

  const [anim, setAnim] = useState(false);
  const bodyRef = useRef<HTMLDivElement>(null);

  /* ---------- ANIMATION ---------- */
  useEffect(() => {
    setAnim(true);
    const t = setTimeout(() => setAnim(false), 350);
    return () => clearTimeout(t);
  }, [otherEmail]);

  /* ---------- AUTO SCROLL ---------- */
  useLayoutEffect(() => {
    if (bodyRef.current) {
      bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
    }
  }, [messages]);

  /* ---------- LOAD USER ---------- */
  useEffect(() => {
    (async () => {
      const data = await accountAPI.get_account_info(otherEmail);
      setUserInfo({
        fullName: data.fullName,
        avatar: data.avatar,
      });
    })();
  }, [otherEmail]);

  /* ---------- IMAGE UPLOAD PREVIEW ---------- */
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files || []);
    if (!selected.length) return;

    const mapped = selected.map((file) => ({
      file,
      url: URL.createObjectURL(file),
    }));

    setImages((prev) => [...prev, ...mapped]);
  };

  /* ---------- FILE UPLOAD PREVIEW ---------- */
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files || []);
    if (!selected.length) return;

    const mapped = selected.map((file) => ({
      file,
      url: URL.createObjectURL(file),
    }));

    setFiles((prev) => [...prev, ...mapped]);
  };

  /* ---------- SEND MESSAGE (UPLOAD FILE_ID ONLY) ---------- */
  const onSend = async () => {
    if (!text.trim() && !images.length && !files.length) return;

    try {
      const mediaIds = await Promise.all(
        images.map((item) =>
          FileService.uploadPicture(item.file).then((r) => r.file_id),
        ),
      );

      const fileIds = await Promise.all(
        files.map((item) =>
          FileService.uploadPicture(item.file).then((r) => r.file_id),
        ),
      );

      await sendMessage(text, fileIds, mediaIds);

      setText("");
      setImages([]);
      setFiles([]);
    } catch (err) {
      console.error("Upload error:", err);
    }
  };
  const removeImage = (index: number) => {
    setImages((prev) => {
      const copy = [...prev];
      URL.revokeObjectURL(copy[index].url);
      copy.splice(index, 1);
      return copy;
    });
  };

  const removeFile = (index: number) => {
    setFiles((prev) => {
      const copy = [...prev];
      URL.revokeObjectURL(copy[index].url);
      copy.splice(index, 1);
      return copy;
    });
  };

  /* ---------- CLEAN URL ---------- */
  useEffect(() => {
    return () => {
      images.forEach((i) => URL.revokeObjectURL(i.url));
      files.forEach((f) => URL.revokeObjectURL(f.url));
    };
  }, [images, files]);

  const goToProfile = (email: string) => {
    window.location.href = `/profile/${email}`;
  };

  const resolveFileUrl = (id: string) =>
    id.startsWith("http") ? id : `${FILE_BASE_URL}/${id}`;

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className={`panel ${anim ? "panel-animate" : ""}`}>
      {/* HEADER */}
      <div className="panel-header">
        <img
          className="postInfoImg"
          src={userInfo?.avatar}
          alt="avatar"
          onClick={() => goToProfile(otherEmail)}
        />
        <div className="postInfoName" onClick={() => goToProfile(otherEmail)}>
          {userInfo?.fullName}
        </div>
      </div>

      {/* BODY */}
      <div className="panel-body" ref={bodyRef}>
        {messages.map((m, i) => (
          <div
            key={m.id || i}
            className={`msg-line ${m.sender_email === me ? "me" : "other"}`}
          >
            <div className="msg-bubble">
              {m.content && <div className="msg-text">{m.content}</div>}
            </div>

            {(m.media ?? []).length > 0 && (
              <div className="msg-media">
                {(m.media ?? []).map((id, idx) => (
                  <img
                    key={idx}
                    src={resolveFileUrl(id)}
                    className="chat-img"
                  />
                ))}
              </div>
            )}

            {(m.file ?? []).length > 0 && (
              <div className="msg-files">
                {(m.file ?? []).map((id, idx) => (
                  <a
                    key={idx}
                    href={resolveFileUrl(id)}
                    className="chat-file"
                    target="_blank"
                    rel="noreferrer"
                  >
                    📎 File {idx + 1}
                  </a>
                ))}
              </div>
            )}
          </div>
        ))}

        {/* PREVIEW */}
        {images.map((img, i) => (
          <div key={i} className="preview-img-wrapper">
            <img src={img.url} className="preview-img" />
            <button className="remove-btn" onClick={() => removeImage(i)}>
              ✕
            </button>
          </div>
        ))}

        {files.map((f, i) => (
          <div key={i} className="preview-file">
            📎 {f.file.name}
            <button className="remove-btn" onClick={() => removeFile(i)}>
              ✕
            </button>
          </div>
        ))}
      </div>

      {/* INPUT */}
      <div className="panel-input">
        <label className="upload-icon">
          <ImageOutlinedIcon />
          <input
            type="file"
            accept="image/*,video/*"
            multiple
            onChange={handleImageUpload}
          />
        </label>

        <label className="upload-icon">
          <AttachFileOutlinedIcon />
          <input type="file" multiple onChange={handleFileUpload} />
        </label>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Nhập tin nhắn..."
          className="chat-input"
        />

        <button onClick={onSend}>
          <SendRoundedIcon />
        </button>
      </div>
    </div>
  );
};

export default MessagePanel;
