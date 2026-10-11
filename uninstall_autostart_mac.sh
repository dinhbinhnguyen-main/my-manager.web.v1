#!/bin/bash
# ==============================================================================
# Script gỡ bỏ tự động khởi động my-manager.web.v1 trên macOS
# ==============================================================================

set -e

PLIST_LABEL="com.mymanager.web"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"

echo "================================================================="
echo " GỠ BỎ TỰ ĐỘNG KHỞI ĐỘNG CÙNG MACOS (my-manager.web.v1)"
echo "================================================================="

if [ -f "$PLIST_PATH" ]; then
    echo "🛑 Đang dừng dịch vụ chạy ngầm..."
    launchctl unload "$PLIST_PATH" 2>/dev/null || true

    echo "🗑️ Đang xóa file cấu hình: $PLIST_PATH"
    rm -f "$PLIST_PATH"

    echo "🎉 Đã gỡ bỏ thành công! Dự án sẽ không tự động bật khi mở máy nữa."
else
    echo "ℹ️ Dịch vụ chưa được cài đặt hoặc đã bị gỡ bỏ trước đó."
fi

echo "================================================================="
