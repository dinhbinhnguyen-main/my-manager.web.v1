# My-Manager Web v1 (`bds-web`)

Website giới thiệu và tìm kiếm Bất Động Sản Đà Lạt hiện đại, hiệu năng cao, siêu nhẹ được xây dựng bằng **FastAPI**, **Jinja2** và **Vanilla CSS/JS**.

Hệ thống kết nối trực tiếp vào cơ sở dữ liệu SQLite `products.db` từ `my-manager.v1` ở chế độ **Read-Only** (không bao giờ gây khóa file hoặc xung đột với ứng dụng quản lý đang chạy) và phục vụ trực tiếp kho hình ảnh thực tế từ thư mục sản phẩm.

---

## Tính Năng Nổi Bật

- 🚀 **Khởi động tức thì (dưới 0.2s)**, tài nguyên RAM tiêu thụ cực thấp (~25MB).
- 🔒 **An toàn dữ liệu tuyệt đối**: Kết nối SQLite URI `?mode=ro`, đảm bảo app desktop `my-manager.v1` có thể ghi/cập nhật dữ liệu đồng thời mà không bị crash.
- 🎨 **Giao diện Cao Cấp (Aesthetic Luxury)**:
  - Tông màu Emerald & Navy kết hợp viền ánh vàng Amber sang trọng.
  - Hiệu ứng kính mờ Glassmorphism, micro-animations và typography sắc nét chuẩn Google Fonts.
  - Bộ lọc đa chiều: Loại giao dịch (Bán / Thuê), Loại hình BĐS, Phường/Xã Đà Lạt, Mức giá, Diện tích, Đường ô tô / xe máy.
  - Sắp xếp linh hoạt (Mới nhất, Giá tăng/giảm, Diện tích).
- 🖼️ **Trình xem ảnh chuyên nghiệp**:
  - Image Carousel & Gallery với danh sách ảnh thu nhỏ.
  - Lightbox toàn màn hình xem ảnh gốc sắc nét, hỗ trợ phím mũi tên và ESC.
  - Tự động ưu tiên ảnh đóng dấu (`with_watermark_<id>`) hoặc ảnh gốc (`source_<id>`).
  - Phục vụ ảnh kèm cache HTTP `Cache-Control` cho tốc độ tải trang cực nhanh.
- 📱 **Tối ưu Mobile & Chuyển đổi**:
  - Thanh liên hệ cố định dưới cùng màn hình (Gọi hotline & Chat Zalo).
  - Tự động soạn sẵn tin nhắn Zalo kèm Mã BĐS (PID).
  - Nút sao chép liên kết nhanh với thông báo Toast.
- ⚡ **REST API đầy đủ**: Cung cấp sẵn endpoint JSON (`/api/products`, `/api/products/{id}`, `/api/health`) sẵn sàng cho Mobile App sau này.

---

## Cấu Trúc Dự Án

```text
my-manager.web.v1/
├── settings.json              # File cấu hình chính (đường dẫn DB, kho ảnh, cổng...)
├── settings.example.json      # File mẫu cấu hình hướng dẫn
├── .env                       # Cấu hình biến môi trường (fallback)
├── .env.example               # Mẫu cấu hình môi trường
├── requirements.txt           # Thư viện Python tối giản
├── run.sh                     # Script 1-click khởi chạy server
├── app/
│   ├── __init__.py
│   ├── config.py              # Đọc cấu hình từ .env
│   ├── constants.py           # Enums, Nhãn tiếng Việt & Danh mục bộ lọc
│   ├── entities.py            # Data Model RealEstateProduct
│   ├── database.py            # Kết nối SQLite Read-Only an toàn
│   ├── services.py            # Truy vấn sản phẩm, bộ lọc, quét ảnh
│   └── main.py                # FastAPI routes (HTML, Image, REST API)
├── templates/                 # Giao diện Jinja2 HTML chuẩn SEO
│   ├── base.html              # Layout chung, Header, Footer, Mobile bar
│   ├── index.html             # Trang chủ, Hero stats, Bộ lọc & Lưới BĐS
│   └── detail.html            # Trang chi tiết, Gallery, Thông số kỹ thuật & Liên hệ
└── static/
    ├── css/
    │   └── style.css          # Hệ thống CSS Design System sang trọng & responsive
    ├── js/
    │   └── main.js            # Tương tác Gallery, Lightbox, Copy link, Tabs
    └── images/
        └── placeholder.svg    # Ảnh dự phòng vector sắc nét
```

---

## Hướng Dẫn Khởi Chạy

### 1. Trên Linux / Máy hiện tại:

```bash
# Kích hoạt virtualenv (đã được tạo sẵn trong thư mục .venv)
source .venv/bin/activate

# Khởi chạy server:
./run.sh
# Hoặc:
uvicorn app.main:app --reload --port 8000
```

Mở trình duyệt: `http://127.0.0.1:8000`

---

### 2. Trên macOS:

Khi chuyển dự án sang máy Mac:

```bash
# Tạo môi trường ảo
python3 -m venv .venv
source .venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt

# Cấu hình file .env
cp .env.example .env
nano .env
```

Chỉnh sửa lại đường dẫn trong `.env` trỏ vào máy Mac của bạn:
```env
# Ví dụ trên macOS:
DB_PATH=/Users/dinhbinhnguyen/Devs/my-manager.v1/bin/products.db
IMAGES_DIR=/Users/dinhbinhnguyen/Devs/my-manager.v1/bin/products
PORT=8000
HOST=127.0.0.1
CONTACT_PHONE=0949940987
CONTACT_ZALO=0949940987
```

Khởi chạy web:
```bash
./run.sh
```

---

## Public Ra Internet Bằng Cloudflare Tunnel (Miễn Phí 100%)

Để gửi cho khách hàng hoặc đối tác xem trên điện thoại ngoài đường:

1. **Cài đặt Cloudflared**:
   - macOS: `brew install cloudflare/cloudflare/cloudflared`
   - Linux: `sudo apt install cloudflared` (hoặc tải binary từ GitHub)

2. **Chạy đường hầm tức thì**:
   ```bash
   cloudflared tunnel --url http://127.0.0.1:8000
   ```
3. Lấy đường dẫn HTTPS (ví dụ: `https://xxx.trycloudflare.com`) để trải nghiệm ngay trên di động.

---

## Tự Động Chạy Web Cùng macOS Khi Khởi Động Máy

### Cách 1: Sử dụng LaunchAgent (Khuyên Dùng - Chạy Ngầm Tàng Hình)
Server sẽ tự động chạy ngầm trong nền ngay khi bạn đăng nhập vào macOS (không cần mở cửa sổ Terminal), và tự động bật lại nếu crash:

1. **Cài đặt (1-click)**:
   ```bash
   ./install_autostart_mac.sh
   ```
2. **Kiểm tra hoạt động**:
   - Truy cập ngay: `http://127.0.0.1:8000`
   - Xem log máy chủ: `tail -f ~/Library/Logs/my-manager.web/output.log`
3. **Gỡ bỏ tự khởi động khi không cần nữa**:
   ```bash
   ./uninstall_autostart_mac.sh
   ```

### Cách 2: Sử dụng Login Items (Hiện Cửa Sổ Terminal)
Nếu bạn muốn nhìn thấy cửa sổ Terminal chạy uvicorn khi vừa bật máy:
1. Mở **System Settings (Cài đặt hệ thống)** trên macOS.
2. Vào **General (Cài đặt chung)** > **Login Items (Mục đăng nhập)**.
3. Nhấn dấu **+** trong phần *"Open at Login"*, chọn file [`Start_Server.command`](file:///home/dinhbinhnguyen/Devs/my-manager.web.v1/Start_Server.command) trong thư mục dự án này.

