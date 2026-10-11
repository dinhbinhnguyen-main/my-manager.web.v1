import os
import re
import io
import zipfile
from typing import List, Optional, Tuple, Dict, Any
from app.database import get_db_connection
from app.entities import RealEstateProduct
from app.config import config
from app.constants import PRICE_RANGES, AREA_RANGES, TRANS_FILTER_CONFIGS

def _extract_sort_key(filename: str):
    """Sắp xếp tự nhiên theo số thứ tự trong tên file ảnh, ví dụ: id_0.jpg, id_1.jpg, id_10.jpg"""
    match = re.search(r'_(\d+)\.[a-zA-Z0-9]+$', filename)
    if match:
        return (0, int(match.group(1)))
    return (1, filename)

def get_product_images(product_id: str, prefer_watermark: Optional[bool] = None) -> List[str]:
    """
    Quét thư mục ảnh theo cấu trúc my-manager.v1:
    - with_watermark_<id>/ hoặc source_<id>/
    Trả về danh sách URL: /images/<product_id>/<filename>
    """
    if prefer_watermark is None:
        prefer_watermark = config.PREFER_WATERMARK

    base_product_dir = os.path.join(config.IMAGES_DIR, product_id)
    if not os.path.isdir(base_product_dir):
        return []

    target_sub = f"with_watermark_{product_id}" if prefer_watermark else f"source_{product_id}"
    fallback_sub = f"source_{product_id}" if prefer_watermark else f"with_watermark_{product_id}"

    target_dir = os.path.join(base_product_dir, target_sub)
    if not os.path.isdir(target_dir) or not any(not f.startswith('.') for f in os.listdir(target_dir)):
        target_dir = os.path.join(base_product_dir, fallback_sub)

    if not os.path.isdir(target_dir):
        return []

    image_files = [
        f for f in os.listdir(target_dir)
        if not f.startswith('.') and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
    ]
    image_files.sort(key=_extract_sort_key)

    return [f"/images/{product_id}/{f}" for f in image_files]

def get_product_image_disk_paths(product_id: str, prefer_watermark: Optional[bool] = None) -> List[str]:
    """
    Trả về danh sách đường dẫn tệp ảnh tuyệt đối trên ổ đĩa
    """
    if prefer_watermark is None:
        prefer_watermark = config.PREFER_WATERMARK

    base_product_dir = os.path.join(config.IMAGES_DIR, product_id)
    if not os.path.isdir(base_product_dir):
        return []

    target_sub = f"with_watermark_{product_id}" if prefer_watermark else f"source_{product_id}"
    fallback_sub = f"source_{product_id}" if prefer_watermark else f"with_watermark_{product_id}"

    target_dir = os.path.join(base_product_dir, target_sub)
    if not os.path.isdir(target_dir) or not any(not f.startswith('.') for f in os.listdir(target_dir)):
        target_dir = os.path.join(base_product_dir, fallback_sub)

    if not os.path.isdir(target_dir):
        return []

    image_files = [
        f for f in os.listdir(target_dir)
        if not f.startswith('.') and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
    ]
    image_files.sort(key=_extract_sort_key)
    return [os.path.join(target_dir, f) for f in image_files]

def create_product_images_zip(product_id: str, prefer_watermark: Optional[bool] = None) -> Optional[io.BytesIO]:
    """
    Đóng gói toàn bộ ảnh của BĐS thành file ZIP trên RAM (BytesIO) để tải về 1-click
    """
    disk_paths = get_product_image_disk_paths(product_id, prefer_watermark)
    if not disk_paths:
        return None

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for idx, file_path in enumerate(disk_paths, 1):
            filename = os.path.basename(file_path)
            arcname = f"{idx:02d}_{filename}"
            zf.write(file_path, arcname=arcname)

    zip_buffer.seek(0)
    return zip_buffer

def find_image_file_path(product_id: str, filename: str) -> Optional[str]:
    """
    Tìm đường dẫn tệp thực tế trên ổ đĩa để phục vụ trực tiếp qua FastAPI FileResponse
    """
    product_dir = os.path.join(config.IMAGES_DIR, product_id)
    if not os.path.isdir(product_dir):
        return None

    order = (
        [f"with_watermark_{product_id}", f"source_{product_id}"]
        if config.PREFER_WATERMARK
        else [f"source_{product_id}", f"with_watermark_{product_id}"]
    )

    for sub in order:
        candidate = os.path.join(product_dir, sub, filename)
        if os.path.isfile(candidate):
            return candidate

    # Kiểm tra cả trường hợp file nằm trực tiếp trong thư mục id
    direct_candidate = os.path.join(product_dir, filename)
    if os.path.isfile(direct_candidate):
        return direct_candidate

    return None

def query_products(
    transaction_type: Optional[str] = None,
    category: Optional[str] = None,
    ward: Optional[str] = None,
    keyword: Optional[str] = None,
    price_range_id: Optional[str] = None,
    area_range_id: Optional[str] = None,
    building_line: Optional[str] = None,
    legal: Optional[str] = None,
    sort_by: str = "newest",
    page: int = 1,
    per_page: int = 12,
    status: str = "selling"
) -> Tuple[List[RealEstateProduct], int, int]:
    """
    Truy vấn danh sách sản phẩm với đầy đủ bộ lọc, phân trang và sắp xếp.
    Trả về: (danh_sách_sản_phẩm, tổng_số_bản_ghi, tổng_số_trang)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    where_clauses = ["status = ?"]
    params: List[Any] = [status]

    if transaction_type and transaction_type != "all":
        where_clauses.append("transaction_type = ?")
        params.append(transaction_type)

    if category and category != "all":
        where_clauses.append("category = ?")
        params.append(category)

    if ward and ward != "all":
        where_clauses.append("ward = ?")
        params.append(ward)

    if building_line and building_line != "all":
        where_clauses.append("building_line = ?")
        params.append(building_line)

    if legal and legal != "all":
        where_clauses.append("legal = ?")
        params.append(legal)

    if keyword and keyword.strip():
        kw = f"%{keyword.strip()}%"
        where_clauses.append("(description LIKE ? OR street LIKE ? OR pid LIKE ? OR phone_number LIKE ?)")
        params.extend([kw, kw, kw, kw])

    # Khoảng giá
    if price_range_id:
        trans_key = transaction_type if transaction_type in TRANS_FILTER_CONFIGS else "sale"
        active_ranges = TRANS_FILTER_CONFIGS.get(trans_key, {}).get("price_ranges", [])

        target_range = next((pr for pr in active_ranges if pr["id"] == price_range_id), None)
        if not target_range:
            for cfg in TRANS_FILTER_CONFIGS.values():
                found = next((pr for pr in cfg["price_ranges"] if pr["id"] == price_range_id), None)
                if found:
                    target_range = found
                    break

        if target_range:
            min_val = target_range["min"]
            max_val = target_range["max"]
            unit_val = target_range.get("unit")
            if trans_key == "rental" or unit_val == "million_per_month":
                where_clauses.append("price >= ? AND price <= ?")
                params.extend([min_val, max_val])
            else:
                where_clauses.append("unit = 'billion' AND price >= ? AND price <= ?")
                params.extend([min_val, max_val])

    # Khoảng diện tích
    if area_range_id:
        for ar in AREA_RANGES:
            if ar["id"] == area_range_id:
                where_clauses.append("area >= ? AND area <= ?")
                params.extend([ar["min"], ar["max"]])
                break

    where_sql = " WHERE " + " AND ".join(where_clauses)

    # Đếm tổng số bản ghi phù hợp
    count_sql = f"SELECT COUNT(*) as total FROM real_estate_products{where_sql}"
    cursor.execute(count_sql, params)
    total_count = cursor.fetchone()["total"]

    # Sắp xếp
    order_sql = " ORDER BY updated_at DESC"
    if sort_by == "price_asc":
        order_sql = " ORDER BY price ASC, updated_at DESC"
    elif sort_by == "price_desc":
        order_sql = " ORDER BY price DESC, updated_at DESC"
    elif sort_by == "area_desc":
        order_sql = " ORDER BY area DESC, updated_at DESC"

    # Phân trang
    offset = max(0, (page - 1) * per_page)
    query_sql = f"SELECT * FROM real_estate_products{where_sql}{order_sql} LIMIT ? OFFSET ?"
    query_params = list(params) + [per_page, offset]

    cursor.execute(query_sql, query_params)
    rows = cursor.fetchall()
    conn.close()

    products = []
    for row in rows:
        p = RealEstateProduct.from_row(row)
        p.images = get_product_images(p.id)
        products.append(p)

    total_pages = max(1, (total_count + per_page - 1) // per_page)
    return products, total_count, total_pages

def get_product_detail(product_id: str) -> Optional[RealEstateProduct]:
    """Lấy chi tiết một sản phẩm theo ID (UUID) hoặc PID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM real_estate_products WHERE id = ? OR pid = ? LIMIT 1",
        (product_id, product_id)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    p = RealEstateProduct.from_row(row)
    p.images = get_product_images(p.id)
    return p

def get_related_products(current_product: RealEstateProduct, limit: int = 4) -> List[RealEstateProduct]:
    """Lấy danh sách các BĐS liên quan cùng khu vực hoặc cùng loại hình"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM real_estate_products 
        WHERE status = 'selling' 
          AND id != ? 
          AND (ward = ? OR category = ?)
        ORDER BY updated_at DESC 
        LIMIT ?
        """,
        (current_product.id, current_product.ward, current_product.category, limit)
    )
    rows = cursor.fetchall()
    conn.close()

    related = []
    for row in rows:
        p = RealEstateProduct.from_row(row)
        p.images = get_product_images(p.id)
        related.append(p)
    return related

def get_market_statistics() -> Dict[str, Any]:
    """Thống kê tổng quan BĐS để hiển thị nhanh trên Hero & Badge"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM real_estate_products WHERE status = 'selling'")
    total_selling = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM real_estate_products 
        WHERE status = 'selling' 
        GROUP BY category 
        ORDER BY count DESC
    """)
    category_counts = {r["category"]: r["count"] for r in cursor.fetchall()}

    cursor.execute("""
        SELECT ward, COUNT(*) as count 
        FROM real_estate_products 
        WHERE status = 'selling' 
        GROUP BY ward 
        ORDER BY count DESC
    """)
    ward_counts = {r["ward"]: r["count"] for r in cursor.fetchall()}

    conn.close()
    return {
        "total_selling": total_selling,
        "category_counts": category_counts,
        "ward_counts": ward_counts,
    }
