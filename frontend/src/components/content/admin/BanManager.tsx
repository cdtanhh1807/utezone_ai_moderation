// components/content/admin/BanManager.tsx
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import styles from './AdminDashboard.module.css';

/* ==================== TYPE DEFINITION ==================== */
type Detail = {
  policyName: string;
  action: string;
  beginAt: string;
  endAt: string;
};

type BanRecord = {
  id: string;
  violatorEmail: string;
  violatorRole: string;
  detail: Detail[];
};

/* ==================== CONSTANTS ==================== */
const LIMIT_PER_PAGE = 20;

/* ==================== COMPONENT ==================== */
const BanManager: React.FC = () => {
  /* ------------- state ------------- */
  const [bans, setBans] = useState<BanRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [page, setPage] = useState(1);
  const [keyword, setKeyword] = useState('');

  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState<BanRecord | null>(null);

  /* suggest */
  const isFocusRef = useRef(false);
  const [showSuggest, setShowSuggest] = useState(false);
  const [suggest, setSuggest] = useState<BanRecord[]>([]);

  /* ------------- fetch real data ------------- */
  useEffect(() => {
    fetch('http://localhost:8000/ban/get_all_ban', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })
      .then(async (r) => {
        const text = await r.text(); // đọc raw trước
        console.log('Raw response:', text);
        if (!text) throw new Error('Body rỗng');
        return JSON.parse(text);   // parse thủ công
      })
      .then((d: BanRecord[]) => {
        console.log('Parsed JSON:', d);
        setBans(d);
        setError(null);
      })
      .catch((e) => {
        console.error('Lỗi thật sự:', e.message);
        setError('Không thể tải danh sách chặn: ' + e.message);
      })
      .finally(() => setLoading(false));
  }, []);

  /* ------------- filtered ------------- */
  const filtered = useMemo(() => {
    let list = bans;
    if (keyword.trim()) {
      const kw = keyword.toLowerCase();
      list = list.filter((b) => b.violatorEmail.toLowerCase().includes(kw));
    }
    return list;
  }, [bans, keyword]);

  const totalPages = Math.ceil(filtered.length / LIMIT_PER_PAGE);
  const pagedList = useMemo(() => {
    const start = (page - 1) * LIMIT_PER_PAGE;
    return filtered.slice(start, start + LIMIT_PER_PAGE);
  }, [filtered, page]);

  /* suggest */
  useEffect(() => {
    if (!keyword.trim()) {
      setSuggest([]);
      setShowSuggest(false);
      return;
    }
    const kw = keyword.toLowerCase();
    const res = filtered.filter((b) => b.violatorEmail.toLowerCase().includes(kw));
    setSuggest(res);
    if (isFocusRef.current) setShowSuggest(res.length > 0);
  }, [keyword, filtered]);

  /* ------------- modal ------------- */
  const openDetail = (b: BanRecord) => {
    setSelected(b);
    document.body.classList.add('modal-open');
    setIsOpen(true);
  };
  const closeModal = () => {
    setIsOpen(false);
    document.body.classList.remove('modal-open');
    setSelected(null);
  };

  /* ------------- render ------------- */
  if (loading) return <div className={styles.page}>Đang tải...</div>;
  if (error) return <div className={styles.page}>Lỗi: {error}</div>;

  return (
    <>
      <div className={styles.page}>
        {/* -------------- Toolbar -------------- */}
        <div className={`${styles.toolbar} ${styles.toolbarBetween}`}>
          <div className={styles.filterLeft}>
            <input
              className={styles.search}
              placeholder="Tìm theo email..."
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
                {suggest.map((b) => (
                  <li
                    key={b.id}
                    onClick={() => {
                      setKeyword(b.violatorEmail);
                      setShowSuggest(false);
                      setPage(1);
                    }}
                  >
                    {b.violatorEmail}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* -------------- Table -------------- */}
        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Email</th>
                <th>Vai trò</th>
                <th>Hành động</th>
              </tr>
            </thead>
            <tbody>
              {pagedList.map((b) => (
                <tr key={b.id}>
                  <td>{b.violatorEmail}</td>
                  <td>{b.violatorRole}</td>
                  <td>
                    <button className={styles.textBtn} onClick={() => openDetail(b)}>
                      Chi tiết
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* -------------- Pagination -------------- */}
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

      {/* -------------- Modal Chi tiết -------------- */}
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
                <div className={styles.modalBody}>
                  {/* Dòng 1 Email */}
                  <div className={styles.formRow}>
                    <div className={styles.formCol}>
                      <label className={styles.label}>Email</label>
                      <input className={styles.input} value={selected?.violatorEmail || ''} disabled />
                    </div>
                  </div>

                  {/* Dòng 2 Lý do */}
                  <label className={styles.label}>Lý do chặn</label>

                  {/* Bảng violations KHÔNG phân trang */}
                  <div className={styles.tableWrapper} style={{ marginTop: 8 }}>
                    <table className={styles.table}>
                      <thead>
                        <tr>
                          <th>Chính sách vi phạm</th>
                          <th>Hình phạt</th>
                          <th>Thời gian vi phạm</th>
                          <th>Thời gian hết hình phạt</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selected?.detail.map((d, idx) => {
                          const isPermanent = d.endAt.startsWith('9999');
                          return (
                            <tr key={idx}>
                              <td>{d.policyName}</td>
                              <td>{d.action}</td>
                              <td>{new Date(d.beginAt).toLocaleString('vi-VN')}</td>
                              <td>{isPermanent ? 'Vĩnh viễn' : new Date(d.endAt).toLocaleString('vi-VN')}</td>
                            </tr>
                          );
                        })}
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
    </>
  );
};

export default BanManager;