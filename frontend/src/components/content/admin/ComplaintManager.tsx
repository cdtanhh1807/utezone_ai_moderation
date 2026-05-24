/* ComplaintManager.tsx */
import React, { useEffect, useMemo, useRef, useState } from "react";
import { Dialog, Transition } from "@headlessui/react";
import { Fragment } from "react";
import styles from "./AdminDashboard.module.css";
import DatePicker from "react-datepicker";
import { vi } from "date-fns/locale";
import "react-datepicker/dist/react-datepicker.css";
import { useNavigate } from "react-router-dom";
import { postAPI } from "../../../services/PostService";
import PostDetail from "../user/post/postDetail";

/* ---------- types ---------- */
type ComplaintItem = {
  _id: string;
  policyId: string;
  policyName: string;
  action: string;
  complainantEmail: string;
  complainantName: string;
  typeContent: "account" | "post" | "comment" | "message";
  contentId: string | null;
  contentParentId: string | null;
  path: string | null;
  content: string | null;
  description: string;
  complaintAt: string;
  approveBy: string;
  approveAt: string;
  verify: boolean | null;
  violation: string[] | null;
};

/* ---------- constants ---------- */
const LIMIT_PER_PAGE = 20;

/* ========== COMPONENT ========== */
const ComplaintManager: React.FC = () => {
  /* ---------- state ---------- */
  const [complaints, setComplaints] = useState<ComplaintItem[]>([]);
  const [page, setPage] = useState(1);

  /* ---------- filter ---------- */
  const [keyword, setKeyword] = useState("");
  const [selectedDate, setSelectedDate] = useState<string>(""); // YYYY-MM-DD

  /* ---------- modal ---------- */
  const [isOpen, setIsOpen] = useState(false);
  const [editing, setEditing] = useState<ComplaintItem | null>(null);
  const navigate = useNavigate();
  const [activePost, setActivePost] = useState<any>(null);
  const [focusCommentId, setFocusCommentId] = useState<string | null>(null);
  const [isPostDetailOpen, setIsPostDetailOpen] = useState(false);

  const isFocusRef = useRef(false);
  const [suggest, setSuggest] = useState<string[]>([]);
  const [showSuggest, setShowSuggest] = useState(false);

  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const showToast = (msg: string, ok: boolean) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 2500);
  };

  /* ---------- fetch data ---------- */
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
      const data: ComplaintItem[] = await res.json();
      setComplaints(data);
    } catch (e) {
      console.error("Lỗi lấy danh sách khiếu nại:", e);
      showToast("Không thể tải danh sách: " + e, false);
    }
  };

  useEffect(() => {
    fetchComplaints();
  }, []);

  /* ---------- filter & phân trang ---------- */
  const filtered = useMemo(() => {
    let list = complaints;

    /* 1. Lọc theo ngày khiếu nại */
    if (selectedDate) {
      const target = new Date(selectedDate);
      list = list.filter((c) => {
        const d = new Date(c.complaintAt);
        return (
          d.getFullYear() === target.getFullYear() &&
          d.getMonth() === target.getMonth() &&
          d.getDate() === target.getDate()
        );
      });
    }

    /* 2. Lọc theo email người khiếu nại */
    if (keyword.trim()) {
      const kw = keyword.toLowerCase();
      list = list.filter((c) => c.complainantEmail.toLowerCase().includes(kw));
    }

    return list;
  }, [complaints, selectedDate, keyword]);

  useEffect(() => {
    if (!keyword.trim()) {
      setSuggest([]);
      setShowSuggest(false);
      return;
    }
    const kw = keyword.toLowerCase();
    const emails = Array.from(
      new Set(filtered.map((c) => c.complainantEmail.toLowerCase()))
    );
    const filteredEmails = emails.filter((e) => e.includes(kw));
    setSuggest(filteredEmails);
    if (isFocusRef.current) setShowSuggest(filteredEmails.length > 0);
  }, [keyword, filtered]);

  const totalPages = useMemo(
    () => Math.ceil(filtered.length / LIMIT_PER_PAGE),
    [filtered]
  );
  const pagedList = useMemo(() => {
    const start = (page - 1) * LIMIT_PER_PAGE;
    return filtered.slice(start, start + LIMIT_PER_PAGE);
  }, [filtered, page]);

  /* ---------- modal ---------- */
  const openDetailModal = (c: ComplaintItem) => {
    setEditing(c);
    document.body.classList.add("modal-open");
    setIsOpen(true);
  };
  const closeModal = () => {
    setIsOpen(false);
    document.body.classList.remove("modal-open");
    setEditing(null);
  };

  /* ---------- API thao tác ---------- */
  const handleReject = async () => {
    if (!editing) return;
    try {
      const res = await fetch(
        `http://localhost:8000/complaint/reject_complaint/${editing._id}`,
        {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      if (!res.ok) throw new Error();
      showToast("Bác bỏ thành công!", true);
      await fetchComplaints();
      setPage(1);
    } catch (e: any) {
      showToast("Bác bỏ thất bại: " + e.message, false);
    }
    closeModal();
  };

  const handleApprove = async () => {
    if (!editing) return;
    try {
      const res = await fetch(
        `http://localhost:8000/complaint/approve_complaint/${editing._id}`,
        {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      if (!res.ok) throw new Error();
      showToast("Phê duyệt thành công!", true);
      await fetchComplaints();
      setPage(1);
    } catch (e: any) {
      showToast("Phê duyệt thất bại: " + e.message, false);
    }
    closeModal();
  };
  const openPostDetailFromComplaint = async (c: ComplaintItem) => {
    try {
      console.log("Mở PostDetail từ Complaint:", c);

      // 1. đóng modal
      closeModal();

      // 2. xác định postId CHUẨN
      const postId = c.contentId;

      if (!postId) {
        console.warn("Không tìm thấy postId");
        return;
      }

      const res = await postAPI.getById(postId);
      const post = res?.post || res;

      console.log("Post lấy được:", post);

      if (!post) {
        console.warn("Không lấy được bài viết");
        return;
      }

      setActivePost(post);

      console.log("Active post set kkkkkkk:", activePost);

      // 5. focus comment nếu cần
      setFocusCommentId(c.typeContent === "comment" ? c.contentId : null);

      // 6. mở PostDetail
      setIsPostDetailOpen(true);
    } catch (err) {
      console.error("Không mở được PostDetail từ Complaint:", err);
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
            <div style={{ position: "relative", display: "inline-block" }}>
              <input
                className={styles.search}
                placeholder="Tìm theo email người khiếu nại"
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
            </div>

            {/* Date picker */}
            <DatePicker
              selected={selectedDate ? new Date(selectedDate) : null}
              onChange={(date: Date | null) =>
                setSelectedDate(date ? date.toISOString().slice(0, 10) : "")
              }
              dateFormat="dd/MM/yyyy"
              placeholderText="Ngày khiếu nại"
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
                <th>Email</th>
                <th>Chính sách</th>
                <th>Hình phạt</th>
                <th>Nội dung</th>
                <th>Thời gian</th>
                <th>Hành động</th>
              </tr>
            </thead>
            <tbody>
              {pagedList.map((c) => (
                <tr key={c._id}>
                  <td>{c.complainantEmail}</td>
                  <td>{c.policyName}</td>
                  <td>{c.action}</td>
                  <td>{c.description}</td>
                  <td>{new Date(c.complaintAt).toLocaleString("vi-VN")}</td>
                  <td>
                    <button
                      className={styles.textBtn}
                      onClick={() => openDetailModal(c)}
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
                  Chi tiết khiếu nại
                </Dialog.Title>

                <div className={styles.modalBody}>
                  {/* ---------- Người khiếu nại ---------- */}
                  <div className={styles.formRow}>
                    <div className={styles.formCol}>
                      <label className={styles.label}>
                        Email người khiếu nại
                      </label>
                      <input
                        className={styles.input}
                        value={editing?.complainantEmail || ""}
                        disabled
                      />
                    </div>
                    <div className={styles.formCol}>
                      <label className={styles.label}>
                        Tên người khiếu nại
                      </label>
                      <input
                        className={styles.input}
                        value={editing?.complainantName || ""}
                        disabled
                      />
                    </div>
                  </div>

                  {/* ---------- ID nội dung (nếu có) ---------- */}
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

                  {/* ---------- Loại & Chính sách ---------- */}
                  <div className={styles.formRow}>
                    <div className={styles.formCol}>
                      <label className={styles.label}>Loại nội dung</label>
                      <input
                        className={styles.input}
                        value={
                          editing?.typeContent === "account"
                            ? "Tài khoản"
                            : editing?.typeContent === "post"
                            ? "Bài viết"
                            : editing?.typeContent === "comment"
                            ? "Bình luận"
                            : "Tin nhắn"
                        }
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

                  {/* ---------- Nội dung khiếu nại ---------- */}
                  <div className={styles.formRow}>
                    <div className={styles.formCol}>
                      <label className={styles.label}>Nội dung khiếu nại</label>
                      <textarea
                        className={styles.textarea}
                        value={editing?.description || ""}
                        disabled
                        rows={3}
                      />
                    </div>
                  </div>

                  {editing?.typeContent &&
                    editing.typeContent !== "message" && (
                      <div className={styles.formRow}>
                        <div className={styles.formCol}>
                          {editing.contentParentId != null ? (
                            // 👉 CÓ contentParentId → hiển thị nội dung dạng textarea (giống mô tả khiếu nại)
                            <>
                              <label className={styles.label}>
                                Nội dung bình luận bị gỡ
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
                            // 👉 KHÔNG CÓ contentParentId → giữ nguyên nút điều hướng
                            <button
                              className={styles.textBtn}
                              onClick={() => {
                                if (!editing) return;

                                if (editing.contentId === null) {
                                  navigate(
                                    `/profile/${editing.complainantEmail}`
                                  );
                                  closeModal();
                                }

                                if (editing.contentParentId === null) {
                                  openPostDetailFromComplaint(editing);
                                }
                              }}
                            >
                              {editing.contentId === null
                                ? "Xem tài khoản"
                                : "Xem bài viết"}
                            </button>
                          )}
                        </div>
                      </div>
                    )}

                  {/* ---------- Người duyệt & thời gian duyệt ---------- */}
                  <div className={styles.formRow}>
                    <div className={styles.formCol}>
                      <label className={styles.label}>
                        Người phê duyệt vi phạm
                      </label>
                      <input
                        className={styles.input}
                        value={editing?.approveBy || ""}
                        disabled
                      />
                    </div>
                    <div className={styles.formCol}>
                      <label className={styles.label}>
                        Thời gian phê duyệt
                      </label>
                      <input
                        className={styles.input}
                        value={
                          editing
                            ? new Date(editing.approveAt).toLocaleString(
                                "vi-VN"
                              )
                            : ""
                        }
                        disabled
                      />
                    </div>
                  </div>

                  {/* ---------- Lịch sử vi phạm ---------- */}
                  <label className={styles.label}>
                    Lịch sử vi phạm chính sách "{editing?.policyName}" của "
                    {editing?.complainantEmail}"
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
                        {(editing?.violation?.length || 0) > 0 ? (
                          editing?.violation?.map((t, i) => (
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
                  <button
                    className={`${styles.textBtn} ${styles.confirm}`}
                    onClick={handleReject}
                  >
                    Bác bỏ
                  </button>
                  <button
                    className={`${styles.textBtn} ${styles.danger}`}
                    onClick={handleApprove}
                  >
                    Phê duyệt
                  </button>
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
            await fetchComplaints();
          }}
          onOpenOriginalPost={async (originalPostId: string) => {
            try {
              const res = await fetch(
                `http://localhost:8000/post/${originalPostId}`
              );
              const originalPost = await res.json();

              // đóng rồi mở lại để reset PostDetail
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

export default ComplaintManager;
