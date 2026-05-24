import React, { useRef, useEffect, useState } from "react";
import "./MusicTrimBar.css";

interface Props {
  duration: number;                  // tổng thời gian file nhạc
  startAt: number;                   // vị trí bắt đầu
  length: number;                    // độ dài đoạn chọn
  onChange: (start: number, len: number) => void;
}

export default function MusicTrimBar({ duration, startAt, length, onChange }: Props) {
  const barRef = useRef<HTMLDivElement | null>(null);

  const [dragging, setDragging] = useState<"left" | "right" | null>(null);

  const handleMouseDown = (side: "left" | "right") => {
    setDragging(side);
  };

  const handleMouseUp = () => {
    setDragging(null);
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!dragging || !barRef.current) return;

    const rect = barRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;

    const percent = Math.max(0, Math.min(1, x / rect.width));
    const time = percent * duration;

    if (dragging === "left") {
      const newStart = Math.min(time, startAt + length - 1);
      onChange(newStart, startAt + length - newStart);
    } else {
      const end = Math.max(startAt + 1, time);
      onChange(startAt, end - startAt);
    }
  };

  useEffect(() => {
    window.addEventListener("mouseup", handleMouseUp);
    window.addEventListener("mousemove", handleMouseMove);

    return () => {
      window.removeEventListener("mouseup", handleMouseUp);
      window.removeEventListener("mousemove", handleMouseMove);
    };
  });

  return (
    <div className="trim-container" ref={barRef}>
      <div className="trim-bg" />

      <div
        className="trim-selected"
        style={{
          left: `${(startAt / duration) * 100}%`,
          width: `${(length / duration) * 100}%`
        }}
      >
        <div className="trim-handle left" onMouseDown={() => handleMouseDown("left")} />
        <div className="trim-handle right" onMouseDown={() => handleMouseDown("right")} />
      </div>
    </div>
  );
}
