import { useState, useRef, useEffect } from "react";
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import "./departmentSelect.css";

const departments = [
    "TẤT CẢ",
  "CHÍNH TRỊ LUẬT",
  "CƠ KHÍ CHẾ TẠO MÁY",
  "CƠ KHÍ ĐỘNG LỰC",
  "CÔNG NGHỆ HÓA HỌC VÀ THỰC PHẨM",
  "CÔNG NGHỆ THÔNG TIN",
  "ĐIỆN - ĐIỆN TỬ",
  "IN VÀ TRUYỀN THÔNG",
  "KHOA HỌC ỨNG DỤNG",
  "KINH TẾ",
  "NGOẠI NGỮ",
  "THỜI TRANG VÀ DU LỊCH",
  "XÂY DỰNG",
  "VIỆN SƯ PHẠM KỸ THUẬT"
];

export default function DepartmentMultiSelect({ selectedDepartments, setSelectedDepartments }: { selectedDepartments: string[], setSelectedDepartments: (vals: string[]) => void }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const toggleSelection = (dept: string) => {
    if (dept === "TẤT CẢ") {
        if (selectedDepartments.includes("TẤT CẢ")) {
        setSelectedDepartments([]);
        } else {
        setSelectedDepartments([...departments]); // chọn tất cả các mục
        }
        return;
    }
    let newSelection: string[] = [];
    if (selectedDepartments.includes(dept)) {
        newSelection = selectedDepartments.filter(d => d !== dept && d !== "TẤT CẢ");
    } else {
        newSelection = [...selectedDepartments.filter(d => d !== "TẤT CẢ"), dept];
    }
    const allSelected = departments.slice(1).every(d => newSelection.includes(d));
    if (allSelected) newSelection = ["TẤT CẢ", ...departments.slice(1)];

    setSelectedDepartments(newSelection);
    };


  return (
    <div className="departmentSelector" ref={menuRef}>
      <span className="dots" onClick={() => setMenuOpen(prev => !prev)}>
        {selectedDepartments.length > 0 ? selectedDepartments.join(" • ") : "Chọn phòng/khoa"} 
        <KeyboardArrowDownIcon />
      </span>

      {menuOpen && (
        <div className="departmentMenu">
          {departments.map((dept) => (
            <div
              key={dept}
              className={`departmentItem ${selectedDepartments.includes(dept) ? "active" : ""}`}
              onClick={() => toggleSelection(dept)}
            >
              {dept} {selectedDepartments.includes(dept) && "•"}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
