import sqlite3
import os
from app.config import config

def get_db_connection():
    """
    Kết nối SQLite ở chế độ URI Read-Only (ro) để không khóa database
    và đọc an toàn tuyệt đối khi tiến trình my-manager.v1 đang ghi.
    """
    db_path = os.path.abspath(config.DB_PATH)
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Không tìm thấy file database SQLite tại: {db_path}")

    uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def check_db_health() -> dict:
    """Kiểm tra tình trạng kết nối DB và đếm sơ bộ số lượng sản phẩm"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM real_estate_products")
        total = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) as selling FROM real_estate_products WHERE status = 'selling'")
        selling = cursor.fetchone()["selling"]
        conn.close()
        return {"status": "ok", "total_products": total, "selling_products": selling}
    except Exception as e:
        return {"status": "error", "message": str(e)}
