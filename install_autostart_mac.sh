#!/bin/bash
# ==============================================================================
# Script tự động đăng ký my-manager.web.v1 khởi động cùng macOS (LaunchAgent)
# Hỗ trợ tự động nhận diện Conda, Virtualenv hoặc Python hệ thống
# ==============================================================================

set -e

# Xác định đường dẫn tuyệt đối đến thư mục dự án
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_LABEL="com.mymanager.web"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
LOG_DIR="$HOME/Library/Logs/my-manager.web"

# Phát hiện môi trường Python hiện tại (Conda hoặc venv)
CURRENT_PYTHON="$(command -v python3 || command -v python || echo "")"
CURRENT_PATH="$PATH"
CURRENT_CONDA_PREFIX="${CONDA_PREFIX:-}"
CURRENT_CONDA_ENV="${CONDA_DEFAULT_ENV:-}"

echo "================================================================="
echo " CÀI ĐẶT TỰ ĐỘNG KHỞI ĐỘNG CÙNG MACOS (my-manager.web.v1)"
echo "================================================================="
echo "📁 Thư mục dự án: $PROJECT_DIR"
if [ -n "$CURRENT_CONDA_ENV" ]; then
    echo "🐍 Phát hiện môi trường Conda: $CURRENT_CONDA_ENV ($CURRENT_CONDA_PREFIX)"
elif [ -n "$VIRTUAL_ENV" ]; then
    echo "🐍 Phát hiện virtualenv: $VIRTUAL_ENV"
else
    echo "🐍 Python hiện tại: $CURRENT_PYTHON"
fi

# 1. Đảm bảo quyền thực thi cho run.sh
chmod +x "$PROJECT_DIR/run.sh"

# 2. Tạo thư mục chứa file LaunchAgent và thư mục Log nếu chưa có
mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "$LOG_DIR"

# 3. Nếu dịch vụ đã chạy trước đó, dỡ bỏ trước khi tạo mới
if launchctl list | grep -q "$PLIST_LABEL"; then
    echo "🔄 Đang dừng dịch vụ cũ..."
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
fi

# 4. Tạo file cấu hình LaunchAgent (.plist) với biến môi trường đầy đủ (đặc biệt cho Conda)
cat <<EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_LABEL}</string>

    <key>WorkingDirectory</key>
    <string>${PROJECT_DIR}</string>

    <!-- Kế thừa biến môi trường (PATH, Conda) để launchd chạy chuẩn xác -->
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>${CURRENT_PATH}:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>CONDA_PREFIX</key>
        <string>${CURRENT_CONDA_PREFIX}</string>
        <key>CONDA_DEFAULT_ENV</key>
        <string>${CURRENT_CONDA_ENV}</string>
        <key>HOME</key>
        <string>${HOME}</string>
    </dict>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>${PROJECT_DIR}/run.sh</string>
    </array>

    <!-- Tự động chạy khi vừa đăng nhập vào macOS -->
    <key>RunAtLoad</key>
    <true/>

    <!-- Luôn duy trì chạy ngầm (tự khởi động lại nếu bị tắt hoặc crash) -->
    <key>KeepAlive</key>
    <true/>

    <!-- Ghi log xuất ra file để dễ kiểm tra -->
    <key>StandardOutPath</key>
    <string>${LOG_DIR}/output.log</string>
    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/error.log</string>
</dict>
</plist>
EOF

echo " Đã tạo file LaunchAgent tại: $PLIST_PATH"

# 5. Kích hoạt dịch vụ ngay lập tức
launchctl load "$PLIST_PATH"

echo "================================================================="
echo "🎉 CÀI ĐẶT THÀNH CÔNG!"
echo " Web server đã được kích hoạt chạy ngầm ngay bây giờ với môi trường của bạn."
echo " Từ nay, mỗi khi bạn mở máy macOS hoặc đăng nhập, web sẽ tự động chạy."
echo ""
echo " Kiểm tra truy cập: http://127.0.0.1:8000"
echo " Xem log hoạt động: tail -f \"$LOG_DIR/output.log\""
echo " Nếu muốn gỡ bỏ tự khởi động: ./uninstall_autostart_mac.sh"
echo "================================================================="
