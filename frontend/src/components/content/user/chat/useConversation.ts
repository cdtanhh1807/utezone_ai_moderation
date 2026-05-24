import { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';
import type { Message } from './useChat';
import useWebSocket from './useWebSocket';
import accountAPI from "../../../../services/AccountService"; 

export type Conversation = {
    other_email: string;
    full_name: string;
    last_message: string;
    last_time: string;
    has_new: boolean;
};

export default function useConversations(selectedEmail?: string | null) {
    const { token, email } = useAuth();
    const [list, setList] = useState<Conversation[]>([]);
    const [loading, setLoading] = useState(true);
    const realtime = useWebSocket(token || '');


    /* ---------- load danh sách ---------- */
    const load = async () => {
        if (!token) return;
        setLoading(true);
        try {
            const { data } = await axios.get<Conversation[]>(
                'http://localhost:8000/message/conversations',
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setList(data.sort((a, b) => new Date(b.last_time).getTime() - new Date(a.last_time).getTime()));
        } catch (e: any) {
            console.error('[useConversations]', e.response?.data || e.message);
        } finally {
            setLoading(false);
        }
    };


    /* ---------- khi có tin NHẬN mới ---------- */
    const handleNewMessage = (msg: Message) => {
        if (msg.sender_email === email) return;

        setList((prev) => {
            const idx = prev.findIndex((c) => c.other_email === msg.sender_email);
            const isActive = selectedEmail === msg.sender_email;

            if (idx === -1) {
                const newConv: Conversation = {
                    other_email: msg.sender_email,
                    full_name: msg.sender_email, // có thể gọi API lấy tên sau
                    last_message: msg.content,
                    last_time: msg.created_at,
                    has_new: !isActive,
                };
                return [newConv, ...prev];
            }

            const updated = [...prev];
            updated[idx] = {
                ...updated[idx],
                last_message: msg.content,
                last_time: msg.created_at,
                has_new: isActive ? false : true,
            };
            return [updated[idx], ...prev.filter((_, i) => i !== idx)];
        });
    };

    useEffect(() => {
        load();
    }, [token]);

    useEffect(() => {
        realtime.forEach((pl) => {
            if (pl.type === 'conversation_update') {
                const conv = pl as Conversation;

                setList((prev) => {
                    const idx = prev.findIndex((c) => c.other_email === conv.other_email);
                    const isActive = selectedEmail === conv.other_email;

                    if (idx === -1) {
                        // Chưa có → thêm đầu
                        return [{ ...conv, has_new: !isActive }, ...prev];
                    }

                    // Đã có → đẩy lên đầu + ghi đè
                    const cloned = [...prev];
                    cloned[idx] = { ...conv, has_new: !isActive };
                    return [cloned[idx], ...prev.filter((_, i) => i !== idx)];
                });
                return; // xong, không xử lý tiếp
            }

            // Còn lại là tin nhắn thường
            if (pl.receiver_email === email) handleNewMessage(pl);
        });
    }, [realtime, email, selectedEmail]);


    /* KHÔNG còn resetUnread nữa */
    return { list, loading, refetch: load };
}