import { useEffect, useState } from "react";
import AccountService from "../../../../services/AccountService";
import { jwtDecode } from "jwt-decode";

export type User = {
  id: string;
  name: string;
  avatar?: string;
};

export const useMention = () => {
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [suggestions, setSuggestions] = useState<User[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [mentionRange, setMentionRange] = useState<{
    start: number;
    end: number;
  } | null>(null);

  const token = localStorage.getItem("token");
  let currentUserEmail: string | null = null;

  if (!currentUserEmail && token) {
    try {
      interface JwtPayload {
        sub: string;
        exp: number;
        per: string;
        role: string;
      }
      const decoded: JwtPayload = jwtDecode<JwtPayload>(token);
      currentUserEmail = decoded.sub;
    } catch (err) {
      console.error("❌ Token không hợp lệ:", err);
    }
  }

  // 🔥 Fetch 1 lần duy nhất
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const relation = await AccountService.get_account_relation(
          currentUserEmail!,
        );

        const emails = relation.followed || [];

        const users = await Promise.all(
          emails.map(async (email: string) => {
            const info = await AccountService.get_account_info(email);

            return {
              id: email, // 🔥 FIX QUAN TRỌNG: lấy từ input
              name: info.fullName || info.username || email,
              avatar: info.avatar,
            };
          }),
        );

        console.log("🔍 Fetched users for mention:", users);

        setAllUsers(users);
      } catch (err) {
        console.error(err);
      }
    };

    if (currentUserEmail) fetchUsers();
  }, [currentUserEmail]);

  // 🔥 Handle input
  const handleChange = (
    e: React.ChangeEvent<HTMLTextAreaElement>,
    setValue: (val: string) => void,
  ) => {
    const value = e.target.value;
    const cursor = e.target.selectionStart;

    setValue(value);

    const textBeforeCursor = value.slice(0, cursor);
    const match = textBeforeCursor.match(/@([^\s@]*)$/);

    if (match) {
      const keyword = match[1].toLowerCase();

      // ⚡ filter local → không gọi API nữa
      const filtered = allUsers.filter((user) =>
        user.name.toLowerCase().includes(keyword),
      );

      setSuggestions(filtered);
      setShowDropdown(true);

      setMentionRange({
        start: cursor - match[0].length,
        end: cursor,
      });
    } else {
      setShowDropdown(false);
      setMentionRange(null);
    }
  };

  // 🔥 chọn user
  const handleSelect = (
    user: User,
    value: string,
    setValue: (val: string) => void,
    textareaRef: React.RefObject<HTMLTextAreaElement>,
    onSelect?: (user: User) => void,
  ) => {
    if (!mentionRange) return;

    const newText =
      value.slice(0, mentionRange.start) +
      `@${user.name}#${user.id} ` +
      value.slice(mentionRange.end);

    setValue(newText);
    setShowDropdown(false);

    // callback ra ngoài nếu cần
    onSelect?.(user);

    setTimeout(() => {
      const pos = mentionRange.start + user.name.length + user.id.length + 3;

      textareaRef.current?.focus();
      textareaRef.current?.setSelectionRange(pos, pos);
    }, 0);
  };

  return {
    suggestions,
    showDropdown,
    handleChange,
    handleSelect,
    mentionRange,
    setMentionRange,
    setSuggestions,
    setShowDropdown,
  };
};
