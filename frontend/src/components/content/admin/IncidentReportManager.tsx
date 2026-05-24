// src/components/content/admin/IncidentReportManager.tsx
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import styles from './AdminDashboard.module.css';
import DatePicker from 'react-datepicker';
import { vi } from 'date-fns/locale';
import 'react-datepicker/dist/react-datepicker.css';
import MySelect from '../../../styles/MySelect'; // 👈 import MySelect

type IncidentReport = {
  _id: string;
  email: string;
  content: string;
  reportedAt: string;
  status: boolean; // false = chưa xử lý, true = đã xử lý
};

const LIMIT_PER_PAGE = 20;

const IncidentReportManager: React.FC = () => {
  const [reports, setReports] = useState<IncidentReport[]>([]);
  const [page, setPage] = useState(1);
  const [keyword, setKeyword] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'resolved'>('all');
  const [selectedDate, setSelectedDate] = useState<string>('');

  const [isOpen, setIsOpen] = useState(false);
  const [selectedReport, setSelectedReport] = useState<IncidentReport | null>(null);

  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const showToast = (msg: string, ok: boolean) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 2500);
  };

  // suggest
  const isFocusRef = useRef(false);
  const [suggest, setSuggest] = useState<string[]>([]);
  const [showSuggest, setShowSuggest] = useState(false);

  const fetchReports = async () => {
    try {
      const res = await fetch('http://localhost:8000/incident_report/get_all_incident_report', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const data = await res.json();
      setReports(data.rs || []);
    } catch (err) {
      console.error('Lỗi tải báo cáo sự cố:', err);
      showToast('Không thể tải danh sách báo cáo', false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  // filter
  const filtered = useMemo(() => {
    let list = reports;

    if (selectedDate) {
      const target = new Date(selectedDate);
      list = list.filter((r) => {
        const d = new Date(r.reportedAt);
        return (
          d.getFullYear() === target.getFullYear() &&
          d.getMonth() === target.getMonth() &&
          d.getDate() === target.getDate()
        );
      });
    }

    if (statusFilter !== 'all') {
      list = list.filter((r) =>
        statusFilter === 'pending' ? r.status === false : r.status === true
      );
    }

    if (keyword.trim()) {
      const kw = keyword.toLowerCase();
      list = list.filter(
        (r) =>
          r.email.toLowerCase().includes(kw) || r.content.toLowerCase().includes(kw)
      );
    }

    return list;
  }, [reports, selectedDate, statusFilter, keyword]);

  const totalPages = Math.ceil(filtered.length / LIMIT_PER_PAGE);
  const pagedList = useMemo(() => {
    const start = (page - 1) * LIMIT_PER_PAGE;
    return filtered.slice(start, start + LIMIT_PER_PAGE);
  }, [filtered, page]);

  // suggest emails
  useEffect(() => {
    if (!keyword.trim()) {
      setSuggest([]);
      setShowSuggest(false);
      return;
    }
    const kw = keyword.toLowerCase();
    const emails = Array.from(new Set(filtered.map((r) => r.email.toLowerCase())));
    const filteredEmails = emails.filter((e) => e.includes(kw));
    setSuggest(filteredEmails);
    if (isFocusRef.current) setShowSuggest(filteredEmails.length > 0);
  }, [keyword, filtered]);

  const openDetail = (report: IncidentReport) => {
    setSelectedReport(report);
    document.body.classList.add('modal-open');
    setIsOpen(true);
  };

  const closeModal = () => {
    setIsOpen(false);
    document.body.classList.remove('modal-open');
    setSelectedReport(null);
  };

  const handleResolve = async () => {
    if (!selectedReport) return;
    try {
      const res = await fetch(`http://localhost:8000/incident_report/update_status/${selectedReport._id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ status: true }),
      });
      if (!res.ok) throw new Error();
      showToast('Đã đánh dấu là đã xử lý', true);
      await fetchReports();
      closeModal();
    } catch (err) {
      showToast('Cập nhật thất bại', false);
    }
  };

  const handleDelete = async () => {
    if (!selectedReport) return;
    if (!window.confirm('Bạn có chắc muốn xóa báo cáo này?')) return;
    try {
      const res = await fetch(`http://localhost:8000/incident_report/delete/${selectedReport._id}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!res.ok) throw new Error();
      showToast('Xóa báo cáo thành công', true);
      await fetchReports();
      closeModal();
    } catch (err) {
      showToast('Xóa thất bại', false);
    }
  };

  return (
    <>
      <div className={styles.page}>
        {/* Toolbar */}
        <div className={`${styles.toolbar} ${styles.toolbarBetween}`}>
          <div className={styles.filterLeft}>
            <div style={{ position: 'relative' }}>
              <input
                className={styles.search}
                placeholder="Tìm theo email hoặc nội dung..."
                value={keyword}
                onChange={(e) => {
                  setKeyword(e.target.value);
                  setPage(1);
                }}
                onFocus={() => {
                  isFocusRef.current = true;
                  if (keyword && suggest.length) setShowSuggest(true);
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

            {/* 👇 Thay thế select bằng MySelect, tăng chiều rộng bằng style hoặc className */}
            <div style={{ minWidth: 180 }}>
              <MySelect
                placeholder="Tất cả trạng thái"
                value={statusFilter}
                onChange={(v) => setStatusFilter(v as any)}
                options={[
                  { value: 'all', label: 'Tất cả trạng thái' },
                  { value: 'pending', label: 'Chưa xử lý' },
                  { value: 'resolved', label: 'Đã xử lý' },
                ]}
              />
            </div>

            <DatePicker
              selected={selectedDate ? new Date(selectedDate) : null}
              onChange={(date: Date | null) =>
                setSelectedDate(date ? date.toISOString().slice(0, 10) : '')
              }
              dateFormat="dd/MM/yyyy"
              placeholderText="Ngày báo cáo"
              locale={vi}
              className={styles.dateInput}
            />
          </div>
        </div>

        {/* Table */}
        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Email</th>
                <th>Nội dung sự cố</th>
                <th>Thời gian</th>
                <th>Trạng thái</th>
                <th>Hành động</th>
              </tr>
            </thead>
            <tbody>
              {pagedList.map((rep) => (
                <tr key={rep._id}>
                  <td>{rep.email}</td>
                  <td>{rep.content.length > 80 ? rep.content.slice(0, 80) + '...' : rep.content}</td>
                  <td>{new Date(rep.reportedAt).toLocaleString('vi-VN')}</td>
                  <td>
                    <span
                      className={`${styles.status} ${
                        rep.status ? styles.stActive : styles.stLocked
                      }`}
                    >
                      {rep.status ? 'Đã xử lý' : 'Chưa xử lý'}
                    </span>
                  </td>
                  <td>
                    <button className={styles.textBtn} onClick={() => openDetail(rep)}>
                      Chi tiết
                    </button>
                  </td>
                </tr>
              ))}
              {pagedList.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center' }}>
                    Không có báo cáo sự cố nào
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className={styles.pagination}>
            <button disabled={page === 1} onClick={() => setPage((p) => p - 1)}>
              Trước
            </button>
            <span>
              {page} / {totalPages}
            </span>
            <button disabled={page === totalPages} onClick={() => setPage((p) => p + 1)}>
              Sau
            </button>
          </div>
        )}
      </div>

      {/* Modal chi tiết */}
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
                  Chi tiết báo cáo sự cố
                </Dialog.Title>

                <div className={styles.modalBody}>
                  <div className={styles.formRow}>
                    <div className={styles.formCol}>
                      <label className={styles.label}>Email người báo cáo</label>
                      <input className={styles.input} value={selectedReport?.email || ''} disabled />
                    </div>
                    <div className={styles.formCol}>
                      <label className={styles.label}>Trạng thái</label>
                      <input
                        className={styles.input}
                        value={selectedReport?.status ? 'Đã xử lý' : 'Chưa xử lý'}
                        disabled
                      />
                    </div>
                  </div>

                  <div className={styles.formRow}>
                    <div className={styles.formCol}>
                      <label className={styles.label}>Thời gian báo cáo</label>
                      <input
                        className={styles.input}
                        value={
                          selectedReport
                            ? new Date(selectedReport.reportedAt).toLocaleString('vi-VN')
                            : ''
                        }
                        disabled
                      />
                    </div>
                  </div>

                  <label className={styles.label}>Nội dung sự cố</label>
                  <textarea
                    className={styles.textarea}
                    rows={5}
                    value={selectedReport?.content || ''}
                    disabled
                  />
                </div>

                <div className={styles.modalFooter}>
                  {selectedReport && !selectedReport.status && (
                    <button className={`${styles.textBtn} ${styles.confirm}`} onClick={handleResolve}>
                      Đánh dấu đã xử lý
                    </button>
                  )}
                  <button className={`${styles.textBtn} ${styles.danger}`} onClick={handleDelete}>
                    Xóa báo cáo
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

      {/* Toast */}
      {toast && (
        <div
          className={`${styles.toast} ${toast.ok ? styles.toastOk : styles.toastErr}`}
        >
          {toast.msg}
        </div>
      )}
    </>
  );
};

export default IncidentReportManager;