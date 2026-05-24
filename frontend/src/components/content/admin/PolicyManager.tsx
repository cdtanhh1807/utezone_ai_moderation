import React, { Fragment, useEffect, useMemo, useRef, useState } from 'react';
import styles from './AdminDashboard.module.css';
import type { Policy, PolicyAction, PolicyLevel, PolicyStatus } from '../../../types/Policy';
import { Dialog, Transition } from '@headlessui/react';
import MySelect from '../../../styles/MySelect';
import { createPortal } from 'react-dom';

const LIMIT_PER_PAGE = 20;

const PolicyManager: React.FC = () => {
  /* ---------- state ---------- */
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [page, setPage] = useState(1);

  /* filter */
  const [keyword, setKeyword] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | PolicyStatus>('all');
  const [levelFilter, setLevelFilter] = useState<'all' | PolicyLevel>('all');

  /* modal & form */
  const [isOpen, setIsOpen] = useState(false);
  const [editing, setEditing] = useState<Policy | null>(null);

  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');
  const [level, setLevel] = useState<PolicyLevel>('1');
  const [status, setStatus] = useState<PolicyStatus>('active');
  const [action, setAction] = useState<PolicyAction>({ permission: '000', detail: '' });
  const [isCustomPenalty, setIsCustomPenalty] = useState(false);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const showToast = (msg: string, ok: boolean) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 2500);
  };

  /* danh sách hình phạt từ API */
  const [penaltyOptions, setPenaltyOptions] = useState<
    { action: PolicyAction }[]
  >([]);

  const api = (endpoint: string, body?: any) =>
    fetch(`http://localhost:8000${endpoint}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(body),
    }).then((r) => {
      if (!r.ok) throw new Error(r.statusText);
      return r.json();
    });

  const [needUnsetAction, setNeedUnsetAction] = useState(false);
  const unsetAction = (policyId: string) =>
    fetch(`http://localhost:8000/policy/unset_action/${policyId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({}),
    }).then((r) => {
      if (!r.ok) throw new Error(r.statusText);
      return r.json();
    });


  /* ---------- fetch policies ---------- */
  useEffect(() => {
    fetch('http://localhost:8000/policy/get_all_policy', {
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
      .then((d) => {
        console.log('Parsed JSON:', d);
        const mapped: Policy[] = d.policy_list.map((p: any) => ({
          id: p._id,
          name: p.name,
          description: p.description,
          level: String(p.level) as PolicyLevel,
          status: p.status as PolicyStatus,
          action: p.action ?? { permission: '000', detail: '' },
          createdAt: p.createdAt,
          updatedAt: p.updatedAt,
        }));
        setPolicies(mapped);
      })
      .catch((e) => {
        console.error('Lỗi thật sự:', e.message);
        showToast('Không thể tải danh sách chính sách: ' + e.message, false);
      });
  }, []);

  /* ---------- fetch penalty list ---------- */
  useEffect(() => {
    fetch('http://localhost:8000/policy/get_all_action', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })
      .then((r) => r.json())
      .then((d) => {
        // đúng tên field trong response
        setPenaltyOptions(d.action_list.map((a: any) => ({ action: a })));
      })
      .catch((e) => console.error('Lỗi khi lấy danh sách hình phạt:', e));
  }, []);

  /* ---------- filter & phân trang ---------- */
  const filtered = useMemo(() => {
    let list = policies;
    if (keyword.trim()) {
      const kw = keyword.toLowerCase();
      list = list.filter(
        (p) =>
          p.name.toLowerCase().includes(kw) ||
          p.description.toLowerCase().includes(kw)
      );
    }
    if (statusFilter !== 'all') list = list.filter((p) => p.status === statusFilter);
    if (levelFilter !== 'all') list = list.filter((p) => p.level === levelFilter);
    return list;
  }, [policies, keyword, statusFilter, levelFilter]);

  const totalPages = Math.ceil(filtered.length / LIMIT_PER_PAGE);
  const pagedList = useMemo(() => {
    const start = (page - 1) * LIMIT_PER_PAGE;
    return filtered.slice(start, start + LIMIT_PER_PAGE);
  }, [filtered, page]);

  /* suggest */
  const [showSuggest, setShowSuggest] = useState(false);
  const [suggest, setSuggest] = useState<Policy[]>([]);
  const isFocusRef = useRef(false);

  useEffect(() => {
    if (!keyword.trim()) { setSuggest([]); setShowSuggest(false); return; }
    const kw = keyword.toLowerCase();
    const res = filtered.filter((p) => p.name.toLowerCase().includes(kw));
    setSuggest(res);
    if (isFocusRef.current) setShowSuggest(res.length > 0);
  }, [keyword, filtered]);

  /* ---------- modal actions ---------- */
  const openAddModal = () => {
    resetForm();
    setEditing(null);
    setIsOpen(true);
    setTimeout(() => document.querySelector<HTMLInputElement>('input[placeholder="Tên chính sách..."]')?.focus(), 0);
  };

  const openEditModal = (p: Policy) => {
    resetForm();
    setEditing(p);
    setName(p.name);
    setDesc(p.description);
    setLevel(p.level);
    setStatus(p.status);

    /* 1. action hiện tại (có thể không còn) */
    const currentAction = p.action ?? { permission: '000', detail: '' };

    /* 2. có nằm trong danh sách không? */
    const inList = penaltyOptions.some((o) => o.action.detail === currentAction.detail);

    if (inList) {
      setAction(currentAction);
      setIsCustomPenalty(false);
    } else {
      /* không nằm trong list → coi như custom */
      setAction({ permission: '000', detail: '' }); // hoặc currentAction nếu muốn giữ text
      setIsCustomPenalty(true);
    }

    document.body.classList.add('modal-open');
    setIsOpen(true);
  };

  const closeModal = () => {
    // setIsOpen(false);
    // document.body.classList.remove('modal-open');
    // resetForm(); setEditing(null);
    setIsOpen(false);
    document.body.classList.remove('modal-open');
    resetForm();
    setEditing(null);
    setNeedUnsetAction(false);
  };

  const resetForm = () => {
    setName(''); setDesc(''); setLevel('1'); setStatus('active');
    setAction({ permission: '000', detail: '' }); setIsCustomPenalty(false);
  };

  const handlePenaltyChange = (val: string) => {
    if (val === '_NONE_') {
      setNeedUnsetAction(true);          // ← ghi nhớ
      setAction({ permission: '000', detail: '' });
      setIsCustomPenalty(false);
      return;
    }

    setNeedUnsetAction(false);           // huỷ flag nếu chọn lại hình phạt khác
    if (val === '_CUSTOM_') {
      setIsCustomPenalty(true);
      setAction({ permission: '000', detail: '' });
      return;
    }
    const selected = penaltyOptions.find((o) => o.action.detail === val);
    setIsCustomPenalty(false);
    setAction(selected?.action ?? { permission: '000', detail: val });
  };

  /* ---------- CRUD handlers ---------- */

  const handleCreate = async () => {
    if (!name.trim()) return showToast('Vui lòng nhập tên chính sách!', false);

    // 2. kiểm tra hình phạt chỉ khi KHÔNG chọn “Không có”
    if (!needUnsetAction && !action.detail.trim())
      return showToast('Vui lòng chọn hình phạt!', false);

    const payload: any = {
      name: name.trim(),
      description: desc.trim(),
      level: parseInt(level, 10),
      status,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    if (!needUnsetAction) payload.action = action; // ➜ 4. chỉ gửi action nếu có

    try {
      const res = await fetch('http://localhost:8000/policy/add_policy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(res.statusText);

      // 5. reload danh sách thực tế từ server
      const { policy_list } = await fetch('http://localhost:8000/policy/get_all_policy', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      })
        .then(r => r.text()).then(t => JSON.parse(t));

      const mapped: Policy[] = policy_list.map((p: any) => ({
        id: p._id,
        name: p.name,
        description: p.description,
        level: String(p.level) as PolicyLevel,
        status: p.status as PolicyStatus,
        action: p.action ?? { permission: '000', detail: '' },
        createdAt: p.createdAt,
        updatedAt: p.updatedAt,
      }));
      setPolicies(mapped);

      showToast('Thêm chính sách thành công!', true);
      closeModal(); // ➜ 6. tự động đóng modal
    } catch (e: any) {
      showToast('Thêm thất bại: ' + e.message, false);
    }
  };

  const handleSave = async () => {
    if (!editing) return;
    if (!name.trim() || (!needUnsetAction && !action.detail.trim()))
      return showToast('Vui lòng điền tên và chọn hình phạt!', false);

    try {
      /* ----- 1. nếu user chọn "Không có" → xóa action trước ----- */
      if (needUnsetAction) {
        await unsetAction(editing.id);
        /* xóa action khỏi local */
        const updatedPolicy = (({ action, ...rest }) => rest as Policy)(editing);
        setPolicies(prev =>
          prev.map(p => (p.id === editing!.id ? updatedPolicy : p))
        );
        setEditing(updatedPolicy);
        /* tiếp tục xuống dưới để update các field khác */
      }
      const currentTime = new Date().toISOString();
      /* ----- 2. update (hoặc tạo mới) các field ----- */
      const payload = {
        name: name.trim(),
        description: desc.trim(),
        level: parseInt(level, 10),
        status,
        updatedAt: currentTime,
        /* chỉ gửi action nếu KHÔNG unset */
        ...(!needUnsetAction && { action }),
      };
      await api(`/policy/update_policy/${editing.id}`, payload);

      /* ----- 3. cập nhật local ----- */
      setPolicies(prev =>
        prev.map(p =>
          p.id === editing!.id
            ? {
              ...p,
              name: payload.name,
              description: payload.description,
              level,
              status: payload.status,
              ...(!needUnsetAction && { action: payload.action }), // chỉ ghi action nếu không unset
              updatedAt: currentTime,
            }
            : p
        )
      );

      showToast('Lưu thành công!', true);
      closeModal();
    } catch (e: any) {
      showToast('Lưu thất bại: ' + e.message, false);
    }
  };

  const ToastPortal = () =>
    toast
      ? createPortal(
        <div className={`${styles.toast} ${toast.ok ? styles.toastOk : styles.toastErr}`}>
          {toast.msg}
        </div>,
        document.body
      )
      : null;

  const RowActions = ({ policy }: { policy: Policy }) => {
    const [ask, setAsk] = useState(false);

    const handleDelete = async () => {
      try {
        await api(`/policy/update_policy/${policy.id}`, { hidden: true });
        setPolicies(prev => prev.filter(x => x.id !== policy.id));
        showToast('Xóa chính sách thành công!', true);
      } catch (e: any) {
        showToast('Xóa thất bại: ' + e.message, false);
      } finally {
        setAsk(false);
      }
    };

    return (
      <>
        <button className={`${styles.textBtn} ${styles.danger}`} onClick={() => setAsk(true)}>
          Xóa
        </button>

        {ask && (
          <div className={styles.confirmOverlay} onClick={() => setAsk(false)}>
            <div className={styles.confirmBox} onClick={(e) => e.stopPropagation()}>
              <div className={styles.confirmTitle}>Xác nhận xóa</div>
              <div className={styles.confirmMsg}>
                Bạn có chắc chắn muốn xóa chính sách <strong>{policy.name}</strong>?
              </div>
              <div className={styles.confirmFooter}>
                <button className={`${styles.textBtn} ${styles.danger}`} onClick={handleDelete}>
                  Xóa
                </button>
                <button className={styles.textBtn} onClick={() => setAsk(false)}>
                  Hủy
                </button>
              </div>
            </div>
          </div>
        )}
      </>
    );
  };

  return (
    <>
      <div className={styles.page}>
        {/* ---------- Toolbar: tìm + lọc + nút ---------- */}
        <div className={`${styles.toolbar} ${styles.toolbarBetween}`}>
          <div className={styles.filterLeft}>
            <input
              className={styles.search}
              placeholder="Tìm theo tên chính sách..."
              value={keyword}
              onChange={(e) => {
                setKeyword(e.target.value);
                setPage(1);
              }}
              onFocus={() => {
                isFocusRef.current = true;
                keyword && suggest.length > 0 && setShowSuggest(true);
              }}
              onBlur={() => {
                isFocusRef.current = false;
                setTimeout(() => setShowSuggest(false), 150);
              }}
            />
            {showSuggest && (
              <ul className={styles.suggestBox}>
                {suggest.map((p) => (
                  <li
                    key={p.id}
                    onClick={() => {
                      setKeyword(p.name);
                      setShowSuggest(false);
                      setPage(1);
                    }}
                  >
                    {p.name}
                  </li>
                ))}
              </ul>
            )}

            <MySelect
              placeholder="Tất cả trạng thái"
              value={statusFilter}
              onChange={(v) => {
                setStatusFilter(v as any);
                setPage(1);
              }}
              options={[
                { value: 'all', label: 'Tất cả trạng thái' },
                { value: 'active', label: 'Bật' },
                { value: 'inactive', label: 'Tắt' },
              ]}
            />

            <MySelect
              placeholder="Tất cả mức độ"
              value={levelFilter}
              onChange={(v) => {
                setLevelFilter(v as any);
                setPage(1);
              }}
              options={[
                { value: 'all', label: 'Tất cả mức độ' },
                { value: '1', label: 'Mức độ 1' },
                { value: '2', label: 'Mức độ 2' },
                { value: '3', label: 'Mức độ 3' },
              ]}
            />
          </div>

          <button className={styles.primaryBtn} onClick={openAddModal}>
            + Thêm chính sách
          </button>
        </div>

        {/* ---------- table ---------- */}
        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Chính sách</th>
                <th className={styles.colDesc}>Mô tả</th>
                <th>Mức độ</th>
                <th>Hình phạt</th>
                <th>Trạng thái</th>
                <th>Ngày tạo</th>
                <th>Ngày cập nhật</th>
                <th>Hành động</th>
              </tr>
            </thead>
            <tbody>
              {pagedList.map((p) => (
                <tr key={p.id}>
                  <td>{p.name}</td>
                  <td className={styles.colDesc}>{p.description}</td>
                  <td>{p.level}</td>
                  {/* <td>{p.action?.detail ?? ''}</td> */}
                  <td>{p.action?.detail || 'Không có'}</td>
                  <td>
                    <span
                      className={`${styles.status} ${p.status === 'active' ? styles.stActive : styles.stLocked
                        }`}
                    >
                      {p.status === 'active' ? 'Bật' : 'Tắt'}
                    </span>
                  </td>
                  <td>{new Date(p.createdAt).toLocaleDateString('vi-VN')}</td>
                  <td>{new Date(p.updatedAt).toLocaleDateString('vi-VN')}</td>
                  <td>
                    <button
                      className={styles.textBtn}
                      onClick={() => openEditModal(p)}
                    >
                      Sửa
                    </button>
                    <RowActions policy={p} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* ---------- pagination ---------- */}
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

      {/* ---------- modal ---------- */}
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
                  <div className={styles.formRow}>
                    <div className={styles.formCol}>
                      <label className={styles.label}>Chính sách</label>
                      <input
                        className={styles.input}
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Tên chính sách..."
                      />
                    </div>

                    <div className={styles.formCol}>
                      <label className={styles.label}>Hình phạt</label>
                      {penaltyOptions.length > 0 && (
                        <MySelect
                          value={
                            penaltyOptions.some((o) => o.action.detail === action.detail)
                              ? action.detail
                              : isCustomPenalty
                                ? '_CUSTOM_'
                                : '_NONE_'
                          }
                          onChange={handlePenaltyChange}
                          options={[
                            { value: '_NONE_', label: 'Không có' },
                            ...penaltyOptions.map((o) => ({
                              value: o.action.detail,
                              label: o.action.detail,
                            })),
                          ]}
                          placeholder=""
                        />
                      )}

                      {/* nếu chưa có dữ liệu → hiển thị select tạm */}
                      {penaltyOptions.length === 0 && (
                        <select
                          className={styles.input}
                          value={action.detail}
                          onChange={(e) => setAction({ ...action, detail: e.target.value })}
                        >
                          <option value="">Không có</option>
                        </select>
                      )}
                    </div>

                    <div className={styles.formCol}>
                      <label className={styles.label}>Trạng thái</label>
                      <MySelect
                        value={status}
                        onChange={(v) => setStatus(v as PolicyStatus)}
                        options={[
                          { value: 'active', label: 'Bật' },
                          { value: 'inactive', label: 'Tắt' },
                        ]}
                        placeholder=""
                      />
                    </div>
                  </div>

                  <label className={styles.label}>Mức độ</label>
                  <MySelect
                    value={level}
                    onChange={(v) => setLevel(v as PolicyLevel)}
                    options={[
                      { value: '1', label: 'Mức độ 1' },
                      { value: '2', label: 'Mức độ 2' },
                      { value: '3', label: 'Mức độ 3' },
                    ]}
                    placeholder=""
                  />

                  <label className={styles.label}>Mô tả</label>
                  <textarea
                    className={styles.textarea}
                    value={desc}
                    onChange={(e) => setDesc(e.target.value)}
                    rows={3}
                    placeholder="Mô tả chi tiết..."
                  />
                </div>

                <div className={styles.modalFooter}>
                  <button
                    className={styles.primaryBtn}
                    onClick={editing ? handleSave : handleCreate}
                  >
                    {editing ? 'Lưu' : 'Tạo'}
                  </button>
                  <button className={styles.textBtn} onClick={closeModal}>
                    Hủy
                  </button>
                </div>
              </Dialog.Panel>
            </div>
          </Transition.Child>
        </Dialog>
      </Transition>

      {/* ---------- toast ---------- */}
      <ToastPortal />
    </>
  );
};

export default PolicyManager;