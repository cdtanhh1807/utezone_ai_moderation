# UTEZone

## 🚀 Tổng quan về Dự án
UTEZone là dự án diễn đàn mạng xã hội được xây dựng đặc biệt dành cho cộng đồng sinh viên Trường Đại học Sư phạm Kỹ thuật TP.HCM (HCMUTE).  
Mục tiêu chính của nền tảng này là giải quyết vấn đề thông tin bị phân mảnh trên nhiều nền tảng khác nhau. UTEZone hướng tới trở thành trung tâm thông tin đáng tin cậy, dễ tiếp nhận và tập trung để sinh viên đăng tải, trao đổi và xác thực thông tin về:

- **Hỗ trợ Học tập** (tài liệu, thảo luận khóa học)
- **Hoạt động của Trường** (sự kiện, tin tức CLB)
- **Kết nối và Tương tác Cộng đồng** (tìm đồng đội, chia sẻ kinh nghiệm)

Hệ thống cũng đặc biệt đẩy mạnh kiểm duyệt nội dung thông qua cơ chế tố cáo và phê duyệt đối với các bài đăng và bình luận, nhằm mang lại một môi trường diễn đàn an toàn, văn minh và tích cực cho toàn thể sinh viên.

## 🛠️ Thiết lập và Cài đặt Dự án
Làm theo các bước dưới đây để thiết lập và chạy dự án UTEZone trên máy tính cục bộ của bạn.

### Yêu cầu Tiên quyết (Prerequisites)
Đảm bảo rằng bạn đã cài đặt các công cụ sau trên hệ thống của mình:

- Git
- Docker và Docker Compose
- Python (dành cho Backend)
- Node.js và npm (dành cho Frontend)

### 1. Clone Repository (Tải Mã nguồn)
Sử dụng Git để tải mã nguồn của dự án:

```bash
git clone https://github.com/cdtanhh1807/UTEZone.git
cd UTEZone
```

### 2. Khởi động Dịch vụ với Docker Compose
Chạy các dịch vụ chính (ví dụ: Cơ sở dữ liệu, Caching) đã được định nghĩa trong file `docker-compose.yml`. Đây là bước thiết yếu đầu tiên.

```bash
docker-compose up -d
```

### 3. Thiết lập Backend
Cài đặt các thư viện cần thiết cho backend:

```bash
pip install -r requirements.txt
```

### 4. Thiết lập Frontend
Di chuyển vào thư mục frontend và cài đặt các module Node cần thiết để chạy ứng dụng:

```bash
npm install
npm audit fix
```

### 5. Tạo kho lưu trữ MinIO
Truy cập:

```bash
http://localhost:9001
```

- Đăng nhập với Username: minioadmin và Password: minioadmin
- Nhấn Create Bucket
- Tên Bucket là ute-zone

## ▶️ Chạy Ứng dụng
Sau khi cài đặt xong các dependencies, bạn cần khởi động máy chủ Backend và Frontend.

### 1. Khởi động Máy chủ Backend
Di chuyển vào thư mục ứng dụng backend/app và khởi động máy chủ bằng lệnh:.

```bash
uvicorn main:app --reload
```

### 2. Khởi động Ứng dụng Frontend
Mở một cửa sổ terminal mới, di chuyển vào thư mục frontend, và chạy lệnh:

```bash
npm run dev
```

### 3. Truy cập ứng dụng
Ứng dụng frontend sẽ mở trong trình duyệt tại http://localhost:5173

Bạn đã có thể bắt đầu sử dụng UTEZone!