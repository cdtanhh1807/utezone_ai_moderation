import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./toast.css";

const ToastProvider = () => {
  return (
    <ToastContainer
      position="top-right"
      autoClose={3000}
      closeOnClick
      pauseOnHover
      hideProgressBar
      newestOnTop
      theme="light"
      style={{ zIndex: 9999999 }} // ✅ đặt z-index cao
    />
  );
};

export default ToastProvider;
