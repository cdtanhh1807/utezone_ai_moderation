import { toast } from "react-toastify";

export const ToastService = {
  success: (msg: string) => toast.success(msg),

  error: (msg: string) => toast.error(msg),

  warning: (msg: string) => toast.warning(msg),

  info: (msg: string) => toast.info(msg),

  confirm: (
    message: string,
    onConfirm: () => void,
    options?: {
      confirmText?: string;
      cancelText?: string;
    }
  ) => {
    toast(
      ({ closeToast }) => (
        <div className="toast-confirm">
          <p className="toast-confirm-message">{message}</p>

          <div className="toast-confirm-actions">
            <button
              className="toast-btn cancel"
              onClick={() => closeToast()}
            >
              {options?.cancelText || "Hủy"}
            </button>

            <button
              className="toast-btn confirm"
              onClick={() => {
                onConfirm();
                closeToast();
              }}
            >
              {options?.confirmText || "Xóa"}
            </button>
          </div>
        </div>
      ),
      {
        autoClose: false,
        closeOnClick: false,
        draggable: false,
      }
    );
  },
};
