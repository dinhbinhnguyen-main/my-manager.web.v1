#!/bin/bash
# ==============================================================================
# Script khởi chạy my-manager.web.v1 (Hỗ trợ toàn diện Conda & Virtualenv trên macOS/Linux)
# ==============================================================================

# Di chuyển về đúng thư mục chứa script
cd "$(dirname "$0")"

# 1. Đọc cấu hình từ file .env nếu có
if [ -f ".env" ]; then
    # Đọc cấu hình biến CONDA_ENV nếu được khai báo
    CONDA_ENV_CUSTOM=$(grep -E '^[[:space:]]*CONDA_ENV=' .env | cut -d '=' -f2- | tr -d '"' | tr -d "'" | tr -d ' ')
fi

# 2. Xử lý môi trường Python (Conda hoặc venv)

# A. Nếu có chỉ định CONDA_ENV cụ thể trong .env
if [ -n "$CONDA_ENV_CUSTOM" ]; then
    # Tìm file kích hoạt conda.sh trên macOS / Linux
    for p in \
        "$HOME/miniconda3/etc/profile.d/conda.sh" \
        "$HOME/miniforge3/etc/profile.d/conda.sh" \
        "$HOME/anaconda3/etc/profile.d/conda.sh" \
        "/opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh" \
        "/opt/homebrew/anaconda3/etc/profile.d/conda.sh" \
        "/usr/local/miniconda3/etc/profile.d/conda.sh" \
        "$CONDA_EXE/../../etc/profile.d/conda.sh"; do
        if [ -f "$p" ]; then
            source "$p"
            break
        fi
    done
    if command -v conda &>/dev/null; then
        echo "⚡ Kích hoạt môi trường Conda: $CONDA_ENV_CUSTOM"
        conda activate "$CONDA_ENV_CUSTOM"
    fi

# B. Nếu đang có sẵn CONDA_PREFIX (do terminal hoặc launchd truyền vào)
elif [ -n "$CONDA_PREFIX" ] && [ -f "$CONDA_PREFIX/bin/python" ]; then
    echo "⚡ Sử dụng môi trường Conda hiện tại: ${CONDA_DEFAULT_ENV:-$CONDA_PREFIX}"
    export PATH="$CONDA_PREFIX/bin:$PATH"

# C. Nếu có virtualenv cục bộ (.venv hoặc venv)
elif [ -d ".venv" ]; then
    echo "⚡ Sử dụng virtualenv: .venv"
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo "⚡ Sử dụng virtualenv: venv"
    source venv/bin/activate

# D. Thử tìm Conda mặc định nếu máy có cài
else
    for p in \
        "$HOME/miniconda3/etc/profile.d/conda.sh" \
        "$HOME/miniforge3/etc/profile.d/conda.sh" \
        "$HOME/anaconda3/etc/profile.d/conda.sh" \
        "/opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh" \
        "/opt/homebrew/anaconda3/etc/profile.d/conda.sh"; do
        if [ -f "$p" ]; then
            source "$p"
            # Nếu có môi trường tên my-manager thì tự kích hoạt
            if conda env list 2>/dev/null | grep -q "^my-manager[[:space:]]"; then
                echo "⚡ Tự động kích hoạt Conda env: my-manager"
                conda activate my-manager
            fi
            break
        fi
    done
fi

# 3. Đọc cấu hình port và host
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}

PY_PATH="$(command -v python3 || command -v python)"

echo "=================================================="
echo "Khởi chạy Web Bất Động Sản Đà Lạt (my-manager.web.v1)"
echo "Python đang dùng: $PY_PATH"
echo "Địa chỉ truy cập: http://127.0.0.1:${PORT}"
echo "=================================================="

# Thực thi uvicorn bằng đúng Python của môi trường đã kích hoạt
if [ -n "$PY_PATH" ]; then
    exec "$PY_PATH" -m uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
else
    exec uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
fi
