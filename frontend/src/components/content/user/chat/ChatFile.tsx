import React, { useEffect, useState } from "react";
import FileService from "../../../../services/FileService";

type Props = { fileId: string; index: number };

const ChatFile: React.FC<Props> = ({ fileId, index }) => {
  const [url, setUrl] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    FileService.getFileUrl(fileId).then((res) => {
      if (!cancelled) setUrl(res.url);
    });
    return () => { cancelled = true; };
  }, [fileId]);

  if (!url) return <span className="chat-file">Loading...</span>;
  return (
    <a href={url} target="_blank" rel="noreferrer" className="chat-file">
      📎 File {index + 1}
    </a>
  );
};

export default ChatFile;
