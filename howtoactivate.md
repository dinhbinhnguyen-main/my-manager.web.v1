Viewed run.sh:1-24
Created run.sh
Viewed install_autostart_mac.sh:1-82
Created install_autostart_mac.sh
Viewed .env.example:1-25
Edited .env.example
Viewed walkthrough.md:150-162
Edited walkthrough.md

Nếu bạn sử dụng **Conda** thay vì `venv` trên macOS, tôi đã nâng cấp toàn bộ hệ thống để **tự động nhận diện Conda 100%**:

---

### Cơ Chế Nhận Diện Conda Tự Động

Khó khăn lớn nhất khi chạy tự động trên macOS với Conda là: trình quản lý chạy ngầm của macOS (`launchd`) hoạt động độc lập và **không nạp file `~/.zshrc`**, nên bình thường hệ thống sẽ báo lỗi không tìm thấy lệnh `conda` hoặc `uvicorn`.

Để xử lý việc này:
1. **[`run.sh`](file:///home/dinhbinhnguyen/Devs/my-manager.web.v1/run.sh)**: Đã được nâng cấp để tự động quét và kích hoạt Conda tại các đường dẫn cài đặt phổ biến trên macOS (`~/miniconda3`, `~/miniforge3`, `~/anaconda3`, `/opt/homebrew/...`).
2. **[`install_autostart_mac.sh`](file:///home/dinhbinhnguyen/Devs/my-manager.web.v1/install_autostart_mac.sh)**: Tự động "bắt" chính xác môi trường Conda bạn đang dùng trong Terminal và truyền trực tiếp vào dịch vụ chạy ngầm của macOS.

---

### Hướng Dẫn Cài Đặt Khởi Động Cho Conda

#### Cách 1: Tự Động Bắt Môi Trường Conda Đang Dùng (Khuyên dùng - Tiện nhất)

1. Mở Terminal trên macOS, kích hoạt môi trường Conda của bạn (nơi bạn đã cài `fastapi`, `uvicorn`...):
   ```bash
   conda activate <tên_môi_trường_của_bạn>
   ```
   *(Ví dụ: `conda activate base` hoặc `conda activate my-manager`)*

2. Di chuyển vào thư mục dự án và chạy script cài đặt:
   ```bash
   cd ~/Devs/my-manager.web.v1
   ./install_autostart_mac.sh
   ```
   Script sẽ tự động in ra:
   > `🐍 Phát hiện môi trường Conda: <tên_env> (/Users/.../miniconda3/envs/...)`
   
   Và dịch vụ ngầm sẽ tự động gắn kết với chính môi trường Conda này.

---

#### Cách 2: Chỉ Định Cố Định Tên Môi Trường Conda Trong File `.env`

Nếu bạn muốn dự án luôn luôn chạy với một môi trường Conda nhất định (kể cả khi bạn chưa `conda activate` trong Terminal):

1. Mở file `.env` trong thư mục dự án, thêm dòng:
   ```env
   CONDA_ENV=tên_môi_trường_conda_của_bạn
   ```
   *(Ví dụ: `CONDA_ENV=my-manager` hoặc `CONDA_ENV=base`)*

2. Chạy lại script cài đặt:
   ```bash
   ./install_autostart_mac.sh
   ```

---

### Kiểm Tra & Quản Lý

- **Kiểm tra web đang chạy**: Mở trình duyệt vào `http://127.0.0.1:8000`.
- **Xem log Conda & Server chạy ngầm**:
  ```bash
  tail -f ~/Library/Logs/my-manager.web/output.log
  ```
- **Khi muốn tắt / gỡ bỏ tự chạy cùng máy**:
  ```bash
  ./uninstall_autostart_mac.sh
  ```