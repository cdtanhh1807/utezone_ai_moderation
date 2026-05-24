import React, { useEffect, useMemo, useState } from 'react';
import styles from './AdminDashboard.module.css';
import type { Account } from '../../../types/Account';
import MySelect from '../../../styles/MySelect';

const LIMIT_PER_PAGE = 20;
const MAX_SUGGEST = 999999999;


/* ---------- Main component ---------- */
const AccountManager: React.FC = () => {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [keyword, setKeyword] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'locked'>('all');
  const [roleFilter, setRoleFilter] = useState<'all' | 'Moderator' | 'User'>('all');
  const [suggest, setSuggest] = useState<Account[]>([]);
  const [showSuggest, setShowSuggest] = useState(false);
  const [page, setPage] = useState(1);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);

  const dbRoleToUiRole = (r: string) => {
    switch (r) {
      case 'Administrator':
        return 'Administrator';
      case 'Moderator':
        return 'Moderator';
      case 'User':
      default:
        return 'User';
    }
  };

  useEffect(() => {
    fetch("http://localhost:8000/account/get_all_account", {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })
      .then((res) => res.json())
      .then((data) => {
        const mapped: Account[] = data.account_list.map((acc: any) => ({
          id: acc._id,
          type: acc.type,
          email: acc.email,
          password: acc.password ?? "",
          role: dbRoleToUiRole(acc.role),
          status: acc.status,
          username: acc.email.split("@")[0],
          userInfo: acc.userInfo ?? {
            fullName: "Chưa cập nhật",
            phone: "",
            address: "",
            email: "",
            day_of_birth: "",
            followers: [],
            limits: [],
            blocks: [],
            description: "",
          },
        }));
        setAccounts(mapped);
      })
      .catch((err) => {
        console.error("Lỗi khi lấy danh sách tài khoản:", err);
        showToast("Không thể tải danh sách tài khoản: " + err, false);
      });
  }, []);

  /* ---------- filter & search ---------- */
  const filtered = useMemo(() => {
    let list = accounts;
    if (keyword.trim()) {
      const kw = keyword.toLowerCase();
      list = list.filter(
        (a) =>
          a.email.toLowerCase().includes(kw) ||
          a.userInfo.fullName.toLowerCase().includes(kw)
      );
    }
    if (statusFilter !== 'all') list = list.filter((a) => a.status === statusFilter);
    if (roleFilter !== 'all') list = list.filter((a) => a.role === roleFilter);
    return list;
  }, [accounts, keyword, statusFilter, roleFilter]);

  const totalPages = Math.ceil(filtered.length / LIMIT_PER_PAGE);
  const pagedList = useMemo(() => {
    const start = (page - 1) * LIMIT_PER_PAGE;
    return filtered.slice(start, start + LIMIT_PER_PAGE);
  }, [filtered, page]);

  /* ---------- suggest ---------- */
  const inputRef = React.useRef<HTMLInputElement>(null);
  const isFocusRef = React.useRef(false);
  useEffect(() => {
    if (!keyword.trim()) {
      setSuggest([]); setShowSuggest(false); return;
    }
    const kw = keyword.toLowerCase();
    const res = filtered
      .filter(
        (a) =>
          a.email.toLowerCase().includes(kw) ||
          a.userInfo.fullName.toLowerCase().includes(kw)
      )
      .slice(0, MAX_SUGGEST);
    setSuggest(res);
    if (isFocusRef.current) setShowSuggest(true);
  }, [keyword, filtered]);

  /* ---------- actions ---------- */
  const showToast = (msg: string, ok: boolean) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 2500);
  };

  /* gọi api update */
  const updateAccountField = async (
    id: string,
    field: 'status' | 'role',
    value: string
  ) => {
    try {
      // Tạo body động
      const body: any = { [field]: value };

      // Nếu update status thì set thêm pernum
      if (field === 'status') {
        if (value === 'locked') {
          body['permission.pernum'] = '000';
        } else if (value === 'active') {
          body['permission.pernum'] = '111';
        }
      }

      const res = await fetch(`http://localhost:8000/account/update_account/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) throw new Error('Cập nhật thất bại');

      const updated = await res.json();

      // Cập nhật lại state local
      setAccounts(prev =>
        prev.map(acc =>
          acc.id === id
            ? {
              ...acc,
              role: updated.account.role,
              status: updated.account.status,
              permission: updated.account.permission, // đồng bộ pernum
            }
            : acc
        )
      );

      showToast('Cập nhật thành công!', true);
    } catch (err) {
      console.error(err);
      showToast('Cập nhật thất bại!', false);
    }
  };

  const toggleStatus = (id: string, newStatus: 'active' | 'locked') => {
    updateAccountField(id, 'status', newStatus);
  };

  const changeRole = (id: string, newRole: 'Moderator' | 'User') => {
    updateAccountField(id, 'role', newRole);
  };

  const removeAccount = async (id: string) => {
    // if (!window.confirm('Bạn có chắc chắn muốn xóa tài khoản này?')) return;

    try {
      const res = await fetch(`http://localhost:8000/account/update_account/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({ 
          hidden: true,
          status: 'locked',
          'permission.pernum': '000', }),
      });

      if (!res.ok) throw new Error('Xóa tài khoản thất bại');

      // Xóa account khỏi state local → giao diện tự động cập nhật
      setAccounts(prev => prev.filter(acc => acc.id !== id));
      showToast('Đã xóa tài khoản!', true);
    } catch (err) {
      console.error(err);
      showToast('Xóa tài khoản thất bại!', false);
    }
  };

  /* ---------- render ---------- */
  return (
    <div className={styles.page}>
      {/* <h2 className={styles.pageTitle}>Quản lý tài khoản</h2> */}

      {/* ---------- toolbar ---------- */}
      <div className={`${styles.toolbar} ${styles.toolbarBetween}`}>
        {/* search + suggest */}
        <div className={styles.filterLeft}>
          <input
            ref={inputRef}
            placeholder="Tìm theo email..."
            className={styles.search}
            value={keyword}
            onChange={(e) => { setKeyword(e.target.value); setPage(1); }}
            onFocus={() => { isFocusRef.current = true; setShowSuggest(true); }}
            onBlur={() => {
              isFocusRef.current = false;
              setTimeout(() => setShowSuggest(false), 150);
            }}
          />
          {showSuggest && suggest.length > 0 && (
            <ul className={styles.suggestBox}>
              {suggest.map((a) => (
                <li key={a.id} onClick={() => { setKeyword(a.email); setShowSuggest(false); setPage(1); }}>
                  {a.userInfo.fullName} ({a.email})
                </li>
              ))}
            </ul>
          )}
          <MySelect
            placeholder="Tất cả trạng thái"
            value={statusFilter}
            onChange={(v: any) => { setStatusFilter(v as any); setPage(1); }}
            options={[
              { value: 'all', label: 'Tất cả trạng thái' },
              { value: 'active', label: 'Hoạt động' },
              { value: 'locked', label: 'Đã khóa' },
            ]}
          />

          {/* filter role */}
          <MySelect
            placeholder="Tất cả vai trò"
            value={roleFilter}
            onChange={(v: any) => { setRoleFilter(v as any); setPage(1); }}
            options={[
              { value: 'all', label: 'Tất cả vai trò' },
              { value: 'Moderator', label: 'Moderator' },
              { value: 'User', label: 'User' },
              { value: 'Administrator', label: 'Administrator' },
            ]}
          />
        </div>
      </div>

      {/* ---------- table ---------- */}
      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Loại tài khoản</th>
              <th>Họ tên</th>
              <th>Email</th>
              <th>Vai trò</th>
              <th>Trạng thái</th>
              <th style={{ width: 220 }}>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {pagedList.map((u) => (
              <tr key={u.id}>
                <td className={styles.capitalize}>{u.type}</td>
                <td>{u.userInfo.fullName}</td>
                <td>{u.email}</td>
                <td>
                  <MySelect
                    value={u.role!}
                    onChange={(v) => changeRole(u.id!, v as any)}
                    options={[
                      { value: 'Moderator', label: 'Moderator' },
                      { value: 'User', label: 'User' },
                      { value: 'Administrator', label: 'Administrator' },
                    ]}
                    placeholder=""
                  />
                </td>
                <td>
                  <span
                    className={`${styles.status} ${u.status === 'active' ? styles.stActive : styles.stLocked
                      }`}
                  >
                    {u.status === 'active' ? 'Hoạt động' : 'Đã khóa'}
                  </span>
                </td>
                <td>
                  <button
                    className={styles.textBtn}
                    disabled={u.status === 'active'}
                    onClick={() => toggleStatus(u.id!, 'active')}
                  >
                    Mở khóa
                  </button>
                  <button
                    className={styles.textBtn}
                    disabled={u.status === 'locked'}
                    onClick={() => toggleStatus(u.id!, 'locked')}
                  >
                    Khóa
                  </button>
                  <button
                    className={`${styles.textBtn} ${styles.danger}`}
                    onClick={() => removeAccount(u.id!)}
                  >
                    Xóa
                  </button>
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
          <button disabled={page === totalPages} onClick={() => setPage((p) => p + 1)}>
            Sau
          </button>
        </div>
      )}

      {/* ---------- toast ---------- */}
      {toast && (
        <div className={`${styles.toast} ${toast.ok ? styles.toastOk : styles.toastErr}`}>
          {toast.msg}
        </div>
      )}
    </div>
  );
};

export default AccountManager;