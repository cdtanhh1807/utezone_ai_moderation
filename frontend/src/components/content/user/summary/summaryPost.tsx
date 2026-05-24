import Draggable from "react-draggable";
import { useRef } from "react";
import "./summaryPost.css";
import logoAI from "../../../../assets/logoAI.png";

interface SummaryBoxProps {
  summary: string;
  onClose: () => void;
}

export default function SummaryBox({ summary, onClose }: SummaryBoxProps) {
  const nodeRef = useRef<HTMLDivElement>(null);

  return (
    <Draggable nodeRef={nodeRef} handle=".summary-header">
      <div ref={nodeRef} className="summary-box">
        <div className="summary-header">
          <div className="ai-title">
            <img src={logoAI} className="ai-avatar" />
            <span className="ai-name">UTE AI</span>
          </div>

          <button className="summary-close" onClick={onClose}>
            ✖
          </button>
        </div>

        <div className="summary-content">{summary}</div>
      </div>
    </Draggable>
  );
}
