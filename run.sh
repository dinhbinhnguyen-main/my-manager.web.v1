#!/bin/bash
# Script khởi chạy nhanh my-manager.web.v1

# Di chuyển về đúng thư mục chứa script
cd "$(dirname "$0")"

# Tự động kích hoạt virtual environment nếu có
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Đọc cấu hình port và host từ file .env nếu có
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}

echo "=================================================="
echo "Khởi chạy Web Bất Động Sản Đà Lạt (my-manager.web.v1)"
echo "Địa chỉ truy cập: http://127.0.0.1:${PORT}"
echo "=================================================="

exec uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
