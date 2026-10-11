from enum import Enum

class ProductStatus(str, Enum):
    SELLING = "selling"
    SOLD = "sold"
    PAUSED = "paused"

class TransactionType(str, Enum):
    SALE = "sale"
    RENTAL = "rental"
    TRANSFER = "transfer"

STATUS_LABELS = {
    "selling": "Đang bán",
    "sold": "Đã bán",
    "paused": "Tạm dừng",
}

TRANSACTION_LABELS = {
    "sale": "Bán",
    "rental": "Cho thuê",
    "transfer": "Chuyển nhượng",
}

CATEGORY_LABELS = {
    "townhouse": "Nhà phố",
    "street_front_house": "Nhà mặt tiền",
    "apartment_condo": "Căn hộ / Chung cư",
    "villa": "Biệt thự",
    "land_plot": "Đất nền",
    "warehouse_yard": "Kho / Xưởng",
    "business_premises": "Mặt bằng kinh doanh",
    "hotel": "Khách sạn",
    "homestay": "Homestay",
}

UNIT_LABELS = {
    "billion": "Tỷ",
    "million": "Triệu",
    "million_per_month": "Triệu/tháng",
}

LEGAL_LABELS = {
    "vi_bang_purchase": "Vi bằng mua bán",
    "shared_agriculture_deed": "Sổ nông nghiệp chung",
    "decentralized_agriculture_deed": "Sổ nông nghiệp phân quyền",
    "private_agriculture_deed": "Sổ nông nghiệp riêng",
    "shared_construction_deed": "Sổ xây dựng chung",
    "decentralized_construction_deed": "Sổ xây dựng phân quyền",
    "private_construction_deed": "Sổ xây dựng riêng",
}

BUILDING_LINE_LABELS = {
    "car_access_road": "Đường ô tô",
    "motorbike_access_road": "Đường xe máy",
}

FURNITURE_LABELS = {
    "no_furniture": "Không nội thất",
    "basic_furniture": "Nội thất cơ bản",
    "full_furniture": "Full nội thất",
}

WARD_LABELS = {
    "phuong_1_xuan_huong": "Phường 1 (Xuân Hương)",
    "phuong_2_xuan_huong": "Phường 2 (Xuân Hương)",
    "phuong_3_xuan_huong": "Phường 3 (Xuân Hương)",
    "phuong_4_xuan_huong": "Phường 4 (Xuân Hương)",
    "phuong_5_cam_ly": "Phường 5 (Cam Ly)",
    "phuong_6_cam_ly": "Phường 6 (Cam Ly)",
    "phuong_7_lang_biang": "Phường 7 (Lang Biang)",
    "phuong_8_lam_vien": "Phường 8 (Lâm Viên)",
    "phuong_9_lam_vien": "Phường 9 (Lâm Viên)",
    "phuong_10_xuan_huong": "Phường 10 (Xuân Hương)",
    "phuong_11_xuan_truong": "Phường 11 (Xuân Trường)",
    "phuong_12_lam_vien": "Phường 12 (Lâm Viên)",
    "xa_xuan_truong": "Xã Xuân Trường",
    "xa_xuan_tho": "Xã Xuân Thọ",
    "xa_ta_nung": "Xã Tà Nung",
    "xa_tram_hanh": "Xã Trạm Hành",
    "thi_tran_lac_duong": "Thị trấn Lạc Dương",
}

TRANS_FILTER_CONFIGS = {
    "all": {
        "title": "Tất Cả Giao Dịch",
        "price_label": "Mức Giá",
        "search_placeholder": "Ví dụ: Phù Đổng Thiên Vương, view đẹp, biệt thự...",
        "price_ranges": [
            {"id": "under_3", "label": "Dưới 3 tỷ", "min": 0, "max": 3, "unit": "billion"},
            {"id": "3_to_6", "label": "3 - 6 tỷ", "min": 3, "max": 6, "unit": "billion"},
            {"id": "6_to_10", "label": "6 - 10 tỷ", "min": 6, "max": 10, "unit": "billion"},
            {"id": "10_to_20", "label": "10 - 20 tỷ", "min": 10, "max": 20, "unit": "billion"},
            {"id": "over_20", "label": "Trên 20 tỷ", "min": 20, "max": 999999, "unit": "billion"},
        ],
    },
    "sale": {
        "title": "Cần Bán",
        "price_label": "Mức Giá Bán",
        "search_placeholder": "Ví dụ: Nhà mặt tiền, biệt thự view rừng thông, đất thổ cư...",
        "price_ranges": [
            {"id": "under_3", "label": "Dưới 3 tỷ", "min": 0, "max": 3, "unit": "billion"},
            {"id": "3_to_6", "label": "3 - 6 tỷ", "min": 3, "max": 6, "unit": "billion"},
            {"id": "6_to_10", "label": "6 - 10 tỷ", "min": 6, "max": 10, "unit": "billion"},
            {"id": "10_to_20", "label": "10 - 20 tỷ", "min": 10, "max": 20, "unit": "billion"},
            {"id": "over_20", "label": "Trên 20 tỷ", "min": 20, "max": 999999, "unit": "billion"},
        ],
    },
    "rental": {
        "title": "Cho Thuê",
        "price_label": "Giá Thuê / Tháng",
        "search_placeholder": "Ví dụ: Căn hộ full nội thất, mặt bằng kinh doanh, homestay...",
        "price_ranges": [
            {"id": "under_3", "label": "0 - 3 triệu/tháng", "min": 0, "max": 3, "unit": "million_per_month"},
            {"id": "3_to_6", "label": "3 - 6 triệu/tháng", "min": 3, "max": 6, "unit": "million_per_month"},
            {"id": "6_to_10", "label": "6 - 10 triệu/tháng", "min": 6, "max": 10, "unit": "million_per_month"},
            {"id": "10_to_20", "label": "10 - 20 triệu/tháng", "min": 10, "max": 20, "unit": "million_per_month"},
            {"id": "20_to_40", "label": "20 - 40 triệu/tháng", "min": 20, "max": 40, "unit": "million_per_month"},
            {"id": "over_40", "label": "Trên 40 triệu/tháng", "min": 40, "max": 999999, "unit": "million_per_month"},
        ],
    },
    "transfer": {
        "title": "Chuyển Nhượng",
        "price_label": "Giá Chuyển Nhượng",
        "search_placeholder": "Ví dụ: Sang nhượng quán cafe, nhà hàng, homestay...",
        "price_ranges": [
            {"id": "under_100m", "label": "Dưới 100 triệu", "min": 0, "max": 0.1, "unit": "billion"},
            {"id": "100m_to_300m", "label": "100 - 300 triệu", "min": 0.1, "max": 0.3, "unit": "billion"},
            {"id": "300m_to_500m", "label": "300 - 500 triệu", "min": 0.3, "max": 0.5, "unit": "billion"},
            {"id": "500m_to_1b", "label": "500 triệu - 1 tỷ", "min": 0.5, "max": 1, "unit": "billion"},
            {"id": "1b_to_3b", "label": "1 - 3 tỷ", "min": 1, "max": 3, "unit": "billion"},
            {"id": "over_3b", "label": "Trên 3 tỷ", "min": 3, "max": 999999, "unit": "billion"},
        ],
    },
}

PRICE_RANGES = TRANS_FILTER_CONFIGS["sale"]["price_ranges"]

AREA_RANGES = [
    {"id": "under_50", "label": "Dưới 50 m²", "min": 0, "max": 50},
    {"id": "50_to_100", "label": "50 - 100 m²", "min": 50, "max": 100},
    {"id": "100_to_200", "label": "100 - 200 m²", "min": 100, "max": 200},
    {"id": "200_to_500", "label": "200 - 500 m²", "min": 200, "max": 500},
    {"id": "over_500", "label": "Trên 500 m²", "min": 500, "max": 999999},
]

SORT_OPTIONS = {
    "newest": "Mới cập nhật",
    "price_asc": "Giá thấp đến cao",
    "price_desc": "Giá cao đến thấp",
    "area_desc": "Diện tích lớn nhất",
}
