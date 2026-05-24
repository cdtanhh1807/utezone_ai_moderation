/* ApproveHistory.tsx */
import React, { useEffect, useMemo, useRef, useState } from "react";
import { Dialog, Transition } from "@headlessui/react";
import { Fragment } from "react";
import styles from "./AdminDashboard.module.css";
import MySelect from "../../../styles/MySelect";
import DatePicker from "react-datepicker";
import { vi } from "date-fns/locale";
import "react-datepicker/dist/react-datepicker.css";
import { useNavigate } from "react-router-dom";
import { postAPI } from "../../../services/PostService";
import PostDetail from "../user/post/postDetail";

/* ---------- types ---------- */
type ApproveReport = {
  policyId: string;
  policyName: string;
  violatorEmail: string;
  violatorName: string;
  typeContent: "account" | "post" | "comment" | "message";
  contentId: string | null;
  contentParentId: string | null;
  content: string | null;
  approveBy: string;
  approveAt: string; // ISO
  violation: string[]; // các thời điểm vi phạm
};

/* ---------- constants ---------- */
const TYPE_LABELS: Record<ApproveReport["typeContent"], string> = {
  account: "Tài khoản",
  post: "Bài viết",
  comment: "Bình luận",
  message: "Tin nhắn",
};
const LIMIT_PER_PAGE = 20;

/* ---------- component ---------- */
const ApproveHistory: React.FC = () => {
  /* ---------- state ---------- */
  const [reports, setReports] = useState<ApproveReport[]>([]);
  const [page, setPage] = useState(1);

  /* ---------- filter ---------- */
  const [keyword, setKeyword] = useState("");
  const [typeFilter, setTypeFilter] = useState<
    "all" | ApproveReport["typeContent"]
  >("all");
  const [selectedDate, setSelectedDate] = useState<string>(""); // YYYY-MM-DD

  /* ---------- modal ---------- */
  const [isOpen, setIsOpen] = useState(false);
  const [editing, setEditing] = useState<ApproveReport | null>(null);
  const [activePost, setActivePost] = useState<any>(null);
  const [focusCommentId, setFocusCommentId] = useState<string | null>(null);
  const [isPostDetailOpen, setIsPostDetailOpen] = useState(false);
  const navigate = useNavigate();

  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const showToast = (msg: string, ok: boolean) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 2500);
  };

  /* ---------- fetch ---------- */
  useEffect(() => {
    fetch(`http://localhost:8000/report/get_all_approve_report`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    })
      .then((r) => r.json())
      .then((data: ApproveReport[]) => setReports(data))
      .catch((err) => {
        console.error("Lỗi khi lấy danh sách:", err);
        showToast("Không thể tải danh sách: " + err, false);
      });
  }, []);

  /* ---------- filter & phân trang ---------- */
  const filtered = useMemo(() => {
    let list = reports;

    /* 1. Lọc theo ngày duyệt (approveAt) */
    if (selectedDate) {
      const target = new Date(selectedDate);
      list = list.filter((r) => {
        const d = new Date(r.approveAt);
        return (
          d.getFullYear() === target.getFullYear() &&
          d.getMonth() === target.getMonth() &&
          d.getDate() === target.getDate()
        );
      });
    }

    /* 2. Lọc theo loại */
    if (typeFilter !== "all")
      list = list.filter((r) => r.typeContent === typeFilter);

    /* 3. Lọc theo email bị tố cáo */
    if (keyword.trim()) {
      const kw = keyword.toLowerCase();
      list = list.filter((r) => r.violatorEmail.toLowerCase().includes(kw));
    }

    return list;
  }, [reports, selectedDate, typeFilter, keyword]);

  const totalPages = useMemo(
    () => Math.ceil(filtered.length / LIMIT_PER_PAGE),
    [filtered]
  );
  const pagedList = useMemo(() => {
    const start = (page - 1) * LIMIT_PER_PAGE;
    return filtered.slice(start, start + LIMIT_PER_PAGE);
  }, [filtered, page]);

  /* ---------- suggest ---------- */
  const isFocusRef = useRef(false);
  const [suggest, setSuggest] = useState<string[]>([]);
  const [showSuggest, setShowSuggest] = useState(false);

  useEffect(() => {
    if (!keyword.trim()) {
      setSuggest([]);
      setShowSuggest(false);
      return;
    }
    const kw = keyword.toLowerCase();
    const allowed = Array.from(
      new Set(filtered.map((r) => r.violatorEmail.toLowerCase()))
    );
    const res = allowed.filter((e) => e.includes(kw));
    setSuggest(res);
    if (isFocusRef.current) setShowSuggest(res.length > 0);
  }, [keyword, filtered]);

  /* ---------- modal ---------- */
  const openDetailModal = (r: ApproveReport) => {
    setEditing(r);
    document.body.classList.add("modal-open");
    setIsOpen(true);
  };
  const closeModal = () => {
    setIsOpen(false);
    document.body.classList.remove("modal-open");
    setEditing(null);
  };
  const openPostDetailFromApprove = async (c: any) => {
    closeModal();

    const postId =
      c.typeContent === "comment" ? c.contentParentId : c.contentId;

    if (!postId) return;

    const res = await postAPI.getById(postId);
    const post = res?.post || res;

    setActivePost(post);
    setFocusCommentId(c.typeContent === "comment" ? c.contentId : null);
    setIsPostDetailOpen(true);
  };
  const fetchComplaints = async () => {
    try {
      const res = await fetch(
        "http://localhost:8000/complaint/get_all_complaint",
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      const data: ApproveReport[] = await res.json();
      setReports(data);
    } catch (e) {
      console.error("Lỗi lấy danh sách khiếu nại:", e);
      showToast("Không thể tải danh sách: " + e, false);
    }
  };

  /* ---------- render ---------- */
  return (
    <>
      <div className={styles.page}>
        {/* ---------- Toolbar ---------- */}
        <div className={`${styles.toolbar} ${styles.toolbarBetween}`}>
          <div className={styles.filterLeft}>
            {/* Search */}
            <input
              className={styles.search}
              placeholder="Tìm theo email tài khoản bị tố cáo"
              value={keyword}
              onChange={(e) => {
                setKeyword(e.target.value);
                setPage(1);
              }}
              onFocus={() => {
                isFocusRef.current = true;
                if (keyword && suggest.length > 0) setShowSuggest(true);
              }}
              onBlur={() => {
                isFocusRef.current = false;
                setTimeout(() => setShowSuggest(false), 150);
              }}
            />
            {showSuggest && (
              <ul className={styles.suggestBox}>
                {suggest.map((email) => (
                  <li
                    key={email}
                    onClick={() => {
                      setKeyword(email);
                      setShowSuggest(false);
                      setPage(1);
                    }}
                  >
                    {email}
                  </li>
                ))}
              </ul>
            )}

            {/* Type filter */}
            <MySelect
              placeholder="Tất cả loại nội dung"
              value={typeFilter}
              onChange={(v: string) => {
                setTypeFilter(v === "all" ? "all" : (v as typeof typeFilter));
                setPage(1);
              }}
              options={[
                { value: "all", label: "Tất cả loại" },
                { value: "account", label: "Tài khoản" },
                { value: "post", label: "Bài viết" },
                { value: "comment", label: "Bình luận" },
                { value: "message", label: "Tin nhắn" },
              ]}
            />

            {/* Date picker duyệt */}
            <DatePicker
              selected={selectedDate ? new Date(selectedDate) : null}
              onChange={(date: Date | null) =>
                setSelectedDate(date ? date.toISOString().slice(0, 10) : "")
              }
              dateFormat="dd/MM/yyyy"
              placeholderText="Ngày duyệt"
              locale={vi}
              className={styles.dateInput}
            />
          </div>
        </div>

        {/* ---------- Table ---------- */}
        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Loại</th>
                <th>Người vi phạm</th>
                <th>Người phê duyệt</th>
                <th>Chính sách</th>
                <th>Thời gian</th>
                <th>Hành động</th>
              </tr>
            </thead>
            <tbody>
              {pagedList.map((r, idx) => (
                <tr key={idx}>
                  <td>{TYPE_LABELS[r.typeContent]}</td>
                  <td>{r.violatorEmail}</td>
                  <td>{r.approveBy}</td>
                  <td>{r.policyName}</td>
                  <td>{new Date(r.approveAt).toLocaleString("vi-VN")}</td>
                  <td>
                    <button
                      className={styles.textBtn}
                      onClick={() => openDetailModal(r)}
                    >
                      Chi tiết
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* ---------- Pagination ---------- */}
        {totalPages > 1 && (
          <div className={styles.pagination}>
            <button disabled={page === 1} onClick={() => setPage((p) => p - 1)}>
              Trước
            </button>
            <span>
              {page} / {totalPages}
            </span>
            <button
              disabled={page === totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              Sau
            </button>
          </div>
        )}
      </div>

      {/* ---------- Modal ---------- */}
      <Transition appear show={isOpen} as={Fragment}>
        <Dialog as="div" className={styles.modalOverlay} onClose={closeModal}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-150"
            enterFrom="opacity-0 scale-95"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-100"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-95"
          >
            <div className={styles.modalContent}>
              <Dialog.Panel className={styles.modalPanel}>
                <Dialog.Title as="h3" className={styles.modalTitle}>
                  Chi tiết tố cáo đã duyệt
                </Dialog.Title>

                <div className={styles.modalBody}>
                  {/* ---------- Người bị tố cáo ---------- */}
                  <div className={styles.formRow}>
                    <div className={styles.formCol}>
                      <label className={styles.label}>
                        {editing?.typeContent === "account"
                          ? "Email bị tố cáo"
                          : "Email chủ nội dung"}
                      </label>
                      <input
                        className={styles.input}
                        value={editing?.violatorEmail || ""}
                        disabled
                      />
                    </div>
                    <div className={styles.formCol}>
                      <label className={styles.label}>Tên</label>
                      <input
                        className={styles.input}
                        value={editing?.violatorName || ""}
                        disabled
                      />
                    </div>
                  </div>

                  {/* ---------- ID động ---------- */}
                  {editing?.typeContent === "post" && (
                    <div className={styles.formRow}>
                      <div className={styles.formCol}>
                        <label className={styles.label}>ID bài viết</label>
                        <input
                          className={styles.input}
                          value={editing.contentId || ""}
                          disabled
                        />
                      </div>
                    </div>
                  )}

                  {editing?.typeContent === "comment" && (
                    <div className={styles.formRow}>
                      <div className={styles.formCol}>
                        <label className={styles.label}>ID bình luận</label>
                        <input
                          className={styles.input}
                          value={editing.contentId || ""}
                          disabled
                        />
                      </div>
                      <div className={styles.formCol}>
                        <label className={styles.label}>Thuộc bài viết</label>
                        <input
                          className={styles.input}
                          value={editing.contentParentId || ""}
                          disabled
                        />
                      </div>
                    </div>
                  )}

                  {editing?.typeContent === "message" && (
                    <div className={styles.formRow}>
                      <div className={styles.formCol}>
                        <label className={styles.label}>ID tin nhắn</label>
                        <input
                          className={styles.input}
                          value={editing.contentId || ""}
                          disabled
                        />
                      </div>
                    </div>
                  )}

                  {/* ---------- Loại & Chính sách ---------- */}
                  <div className={styles.formRow}>
                    <div className={styles.formCol}>
                      <label className={styles.label}>Loại nội dung</label>
                      <input
                        className={styles.input}
                        value={editing ? TYPE_LABELS[editing.typeContent] : ""}
                        disabled
                      />
                    </div>
                    <div className={styles.formCol}>
                      <label className={styles.label}>Chính sách vi phạm</label>
                      <input
                        className={styles.input}
                        value={editing?.policyName || ""}
                        disabled
                      />
                    </div>
                  </div>

                  {/* ---------- Nội dung (nếu có) ---------- */}
                  {editing?.typeContent === "message" && (
                    <div className={styles.formRow}>
                      <div className={styles.formCol}>
                        <label className={styles.label}>
                          Nội dung tin nhắn
                        </label>
                        <input
                          className={styles.input}
                          value={editing.content || ""}
                          disabled
                        />
                      </div>
                    </div>
                  )}

                  {/* ---------- Nút Xem… ---------- */}
                  {editing?.typeContent &&
                    editing.typeContent !== "message" && (
                      <div className={styles.formRow}>
                        <div className={styles.formCol}>
                          {editing.contentParentId != null ? (
                            <>
                              <label className={styles.label}>
                                Nội dung bình luận bị tố cáo
                              </label>
                              <textarea
                                className={styles.textarea}
                                value={
                                  editing.content ||
                                  "Không có nội dung hiển thị"
                                }
                                disabled
                                rows={3}
                              />
                            </>
                          ) : (
                            <button
                              className={styles.textBtn}
                              onClick={() => {
                                if (!editing) return;

                                // xem tài khoản
                                if (editing.typeContent === "account") {
                                  navigate(`/profile/${editing.violatorEmail}`);
                                  closeModal();
                                  return;
                                }

                                // xem post (post hoặc comment đều dùng chung hàm)
                                if (
                                  editing.contentParentId === null
                                ) {
                                  openPostDetailFromApprove(editing);
                                }
                              }}
                            >
                              {editing.typeContent === "account"
                                ? "Xem tài khoản bị tố cáo"
                                : editing.typeContent === "post"
                                ? "Xem bài viết"
                                : "Xem bình luận"}
                            </button>
                          )}
                        </div>
                      </div>
                    )}

                  {/* ---------- Lịch sử vi phạm ---------- */}
                  <label className={styles.label}>
                    Lịch sử vi phạm chính sách "{editing?.policyName}" của "
                    {editing?.violatorEmail}"
                  </label>
                  <div className={styles.tableWrapper} style={{ marginTop: 8 }}>
                    <table className={styles.table}>
                      <thead>
                        <tr>
                          <th>Số lần vi phạm</th>
                          <th>Thời gian</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(editing?.violation.length || 0) > 0 ? (
                          editing?.violation.map((t, i) => (
                            <tr key={i}>
                              <td>{i + 1}</td>
                              <td>{new Date(t).toLocaleString("vi-VN")}</td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td>
                              <b>0</b>
                            </td>
                            <td>Không có lịch sử vi phạm</td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className={styles.modalFooter}>
                  <button className={styles.textBtn} onClick={closeModal}>
                    Đóng
                  </button>
                </div>
              </Dialog.Panel>
            </div>
          </Transition.Child>
        </Dialog>
      </Transition>

      {toast && (
        <div
          className={`${styles.toast} ${
            toast.ok ? styles.toastOk : styles.toastErr
          }`}
        >
          {toast.msg}
        </div>
      )}
      {isPostDetailOpen && activePost && (
        <PostDetail
          activePost={activePost}
          focusCommentId={focusCommentId}
          onClose={() => setIsPostDetailOpen(false)}
          onCommentAdded={async () => {
              // reload danh sách complaint sau khi thêm comment (nếu cần)
              await fetchComplaints();
            }}
          onOpenOriginalPost={async (originalPostId: string) => {
            try {
              const res = await fetch(
                `http://localhost:8000/post/${originalPostId}`
              );
              const originalPost = await res.json();

              setIsPostDetailOpen(false);
              requestAnimationFrame(() => {
                setActivePost(originalPost);
                setIsPostDetailOpen(true);
              });
            } catch (err) {
              console.error("Không lấy được bài viết gốc", err);
            }
          }}
        />
      )}
    </>
  );
};

export default ApproveHistory;
