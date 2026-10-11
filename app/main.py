import os
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import config
from app.services import (
    query_products,
    get_product_detail,
    get_related_products,
    find_image_file_path,
    get_market_statistics,
    create_product_images_zip
)
from app.ai_service import gemini_service, AIPromptHelper
import json
from app.constants import (
    TRANSACTION_LABELS,
    CATEGORY_LABELS,
    WARD_LABELS,
    PRICE_RANGES,
    TRANS_FILTER_CONFIGS,
    AREA_RANGES,
    SORT_OPTIONS,
    BUILDING_LINE_LABELS,
    LEGAL_LABELS,
    STATUS_LABELS
)
from app.database import check_db_health

# Khởi tạo FastAPI App
app = FastAPI(
    title=config.SITE_NAME,
    description="Hệ thống Website Bất Động Sản Đà Lạt - Hiệu năng cao & Tinh gọn",
    version="1.0.0"
)

# Tạo thư mục static và templates nếu chưa có
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/images", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount thư mục tĩnh
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ==========================================
# ENDPOINT PHỤC VỤ ẢNH BĐS TRỰC TIẾP
# ==========================================
@app.get("/images/{product_id}/{filename}", name="serve_product_image")
async def serve_product_image(product_id: str, filename: str, download: bool = False):
    """
    Phục vụ tệp ảnh từ kho lưu trữ của my-manager.v1.
    Có Cache-Control header để trình duyệt lưu cache tải cực nhanh.
    Hỗ trợ tải trực tiếp về thiết bị với Content-Disposition qua query param ?download=1.
    """
    file_path = find_image_file_path(product_id, filename)
    if not file_path or not os.path.exists(file_path):
        # Trả về placeholder nếu không tìm thấy file
        placeholder_path = os.path.join("static", "images", "placeholder.svg")
        if os.path.exists(placeholder_path):
            return FileResponse(placeholder_path, media_type="image/svg+xml")
        raise HTTPException(status_code=404, detail="Ảnh không tồn tại")

    ext = os.path.splitext(filename)[1].lower()
    media_type = "image/jpeg"
    if ext == ".png":
        media_type = "image/png"
    elif ext == ".webp":
        media_type = "image/webp"

    headers = {"Cache-Control": "public, max-age=604800, immutable"}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'

    return FileResponse(
        file_path,
        media_type=media_type,
        headers=headers
    )


# ==========================================
# GIAO DIỆN WEB (HTML)
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def home_page(
    request: Request,
    trans: str = Query("all", description="Loại giao dịch (sale, rental, all)"),
    category: str = Query("all", description="Loại BĐS"),
    ward: str = Query("all", description="Phường / Xã"),
    price: str = Query("", description="Mã khoảng giá"),
    area: str = Query("", description="Mã khoảng diện tích"),
    line: str = Query("all", description="Đường ô tô / xe máy"),
    legal: str = Query("all", description="Pháp lý"),
    sort: str = Query("newest", description="Thứ tự sắp xếp"),
    q: str = Query("", description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1, description="Trang hiện tại")
):
    """Trang chủ hiển thị danh sách BĐS với bộ lọc đa tiêu chí và phân trang"""
    products, total_count, total_pages = query_products(
        transaction_type=trans if trans != "all" else None,
        category=category if category != "all" else None,
        ward=ward if ward != "all" else None,
        keyword=q if q.strip() else None,
        price_range_id=price if price else None,
        area_range_id=area if area else None,
        building_line=line if line != "all" else None,
        legal=legal if legal != "all" else None,
        sort_by=sort,
        page=page,
        per_page=12
    )

    stats = get_market_statistics()

    trans_config = TRANS_FILTER_CONFIGS.get(trans, TRANS_FILTER_CONFIGS.get("all", TRANS_FILTER_CONFIGS["sale"]))
    current_price_ranges = trans_config.get("price_ranges", [])
    current_price_label = trans_config.get("price_label", "Mức Giá")
    current_placeholder = trans_config.get("search_placeholder", "Ví dụ: Phù Đổng Thiên Vương, view đẹp...")

    active_filter_count = sum([
        1 if trans and trans != "all" else 0,
        1 if category and category != "all" else 0,
        1 if ward and ward != "all" else 0,
        1 if price else 0,
        1 if area else 0,
        1 if line and line != "all" else 0,
        1 if q and q.strip() else 0,
    ])

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "products": products,
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "active_filter_count": active_filter_count,
            # Trạng thái lọc
            "selected_trans": trans,
            "selected_cat": category,
            "selected_ward": ward,
            "selected_price": price,
            "selected_area": area,
            "selected_line": line,
            "selected_legal": legal,
            "selected_sort": sort,
            "search_query": q,
            # Danh mục tùy chọn & Cấu hình bộ lọc theo từng tab
            "trans_options": TRANSACTION_LABELS,
            "cat_options": CATEGORY_LABELS,
            "ward_options": WARD_LABELS,
            "price_ranges": current_price_ranges,
            "price_label": current_price_label,
            "search_placeholder": current_placeholder,
            "trans_filter_configs": TRANS_FILTER_CONFIGS,
            "trans_filter_configs_json": json.dumps(TRANS_FILTER_CONFIGS, ensure_ascii=False),
            "area_ranges": AREA_RANGES,
            "sort_options": SORT_OPTIONS,
            "line_options": BUILDING_LINE_LABELS,
            "legal_options": LEGAL_LABELS,
            # Thông tin liên hệ & Thống kê
            "stats": stats,
            "site_name": config.SITE_NAME,
            "contact_phone": config.CONTACT_PHONE,
            "contact_zalo": config.CONTACT_ZALO,
        }
    )


@app.get("/property/{product_id}", response_class=HTMLResponse)
async def detail_page(request: Request, product_id: str):
    """Trang chi tiết sản phẩm BĐS với Gallery ảnh, thông số kỹ thuật, mô tả đầy đủ"""
    product = get_product_detail(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm BĐS không tồn tại hoặc đã ngừng giao dịch")

    related = get_related_products(product, limit=4)
    angles = AIPromptHelper.get_angles()

    return templates.TemplateResponse(
        request=request,
        name="detail.html",
        context={
            "p": product,
            "related": related,
            "angles": angles,
            "site_name": config.SITE_NAME,
            "contact_phone": config.CONTACT_PHONE,
            "contact_zalo": config.CONTACT_ZALO,
        }
    )


@app.get("/property/{product_id}/download-images", name="download_product_images")
async def download_product_images(product_id: str):
    """
    Tải toàn bộ hình ảnh của BĐS dưới dạng file ZIP nén sẵn trên RAM.
    Hoạt động 1-click mượt mà trên cả điện thoại (iOS, Android) và máy tính (Desktop).
    """
    product = get_product_detail(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm BĐS không tồn tại")

    zip_buffer = create_product_images_zip(product.id)
    if not zip_buffer:
        raise HTTPException(status_code=404, detail="Sản phẩm này chưa có hình ảnh để tải về")

    filename = f"{product.pid or product.id[:8]}_images.zip"
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache"
        }
    )


@app.post("/api/products/{product_id}/ai-rewrite")
async def api_ai_rewrite_product(request: Request, product_id: str):
    """
    Gọi Gemini AI để viết lại tiêu đề và mô tả BĐS chuẩn SEO Facebook,
    tuân thủ nghiêm ngặt chính sách Meta và chống spam giống hệt repo my-manager.v1.
    """
    product = get_product_detail(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm BĐS không tồn tại")

    angle_name = None
    try:
        body = await request.json()
        angle_name = body.get("angle")
    except Exception:
        pass

    try:
        result = await gemini_service.rewrite_real_estate(
            raw_title=product.display_title,
            raw_desc=product.description or f"{product.display_title}. Diện tích: {product.formatted_area}. Pháp lý: {product.legal_label}. Đường xe: {product.building_line_label}.",
            is_rental=(product.transaction_type == "rental"),
            angle_name=angle_name,
            contact_phone=config.CONTACT_PHONE
        )
        return {
            "status": "success",
            "title": result["title"],
            "description": result["description"],
            "angle": result["angle"],
            "product_id": product.id,
            "pid": product.pid
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Lỗi tạo nội dung AI: {str(e)}"
            }
        )


# ==========================================
# REST API (JSON)
# ==========================================
@app.get("/api/products")
async def api_list_products(
    trans: Optional[str] = None,
    category: Optional[str] = None,
    ward: Optional[str] = None,
    q: Optional[str] = None,
    page: int = 1,
    per_page: int = 20
):
    """API JSON lấy danh sách BĐS"""
    products, total_count, total_pages = query_products(
        transaction_type=trans,
        category=category,
        ward=ward,
        keyword=q,
        page=page,
        per_page=per_page
    )
    return {
        "total": total_count,
        "page": page,
        "total_pages": total_pages,
        "items": [
            {
                "id": p.id,
                "pid": p.pid,
                "title": p.display_title,
                "transaction_type": p.transaction_type,
                "transaction_label": p.transaction_label,
                "category": p.category,
                "category_label": p.category_label,
                "ward": p.ward,
                "ward_label": p.ward_label,
                "street": p.street_display,
                "price": p.price,
                "unit": p.unit,
                "formatted_price": p.formatted_price,
                "area": p.area,
                "formatted_area": p.formatted_area,
                "legal": p.legal,
                "legal_label": p.legal_label,
                "building_line": p.building_line,
                "building_line_label": p.building_line_label,
                "images": p.images,
                "cover_image": p.primary_image,
                "updated_at": p.updated_at
            }
            for p in products
        ]
    }


@app.get("/api/products/{product_id}")
async def api_product_detail(product_id: str):
    """API JSON lấy chi tiết một BĐS"""
    p = get_product_detail(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    return {
        "id": p.id,
        "pid": p.pid,
        "title": p.display_title,
        "status": p.status,
        "status_label": p.status_label,
        "transaction_type": p.transaction_type,
        "transaction_label": p.transaction_label,
        "category": p.category,
        "category_label": p.category_label,
        "ward": p.ward,
        "ward_label": p.ward_label,
        "street": p.street_display,
        "address": p.display_address,
        "price": p.price,
        "unit": p.unit,
        "formatted_price": p.formatted_price,
        "price_per_m2": p.price_per_m2,
        "area": p.area,
        "formatted_area": p.formatted_area,
        "legal": p.legal,
        "legal_label": p.legal_label,
        "structure": p.structure,
        "structure_display": p.structure_display,
        "function": p.function,
        "building_line": p.building_line,
        "building_line_label": p.building_line_label,
        "furniture": p.furniture,
        "furniture_label": p.furniture_label,
        "description": p.description,
        "phone_number": p.phone_number,
        "images": p.images,
        "created_at": p.created_at,
        "updated_at": p.updated_at
    }


@app.get("/api/health")
async def api_health():
    """Kiểm tra tình trạng hoạt động và cấu hình database"""
    return {
        "app": "my-manager.web.v1",
        "status": "online",
        "config_source": config.source,
        "database": check_db_health(),
        "db_path": config.DB_PATH,
        "db_path_exists": os.path.exists(config.DB_PATH),
        "images_dir": config.IMAGES_DIR,
        "images_dir_exists": os.path.exists(config.IMAGES_DIR)
    }

