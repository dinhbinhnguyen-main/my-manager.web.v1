from dataclasses import dataclass, field
from typing import Optional, List
from app.constants import (
    TRANSACTION_LABELS, CATEGORY_LABELS, UNIT_LABELS,
    LEGAL_LABELS, BUILDING_LINE_LABELS, FURNITURE_LABELS,
    WARD_LABELS, STATUS_LABELS
)

@dataclass
class RealEstateProduct:
    id: str
    pid: str
    status: str
    transaction_type: str
    province: str
    district: str
    ward: str
    street: str
    phone_number: str
    category: str
    area: float
    price: float
    unit: str
    legal: str
    structure: float
    function: str
    building_line: str
    furniture: str
    description: str
    created_at: str
    updated_at: str
    images: List[str] = field(default_factory=list)

    @property
    def formatted_price(self) -> str:
        if self.transaction_type == "rental":
            unit_str = "Triệu/tháng"
        else:
            unit_str = UNIT_LABELS.get(self.unit, self.unit)
        if self.price <= 0:
            return "Thỏa thuận"
        if self.price == int(self.price):
            return f"{int(self.price)} {unit_str}"
        return f"{self.price:.2f}".rstrip("0").rstrip(".") + f" {unit_str}"

    @property
    def price_per_m2(self) -> str:
        if self.transaction_type == "rental":
            return ""
        if self.area <= 0 or self.price <= 0:
            return ""
        if self.unit == "billion":
            val = (self.price * 1000.0) / self.area
            return f"~{val:.1f} tr/m²"
        elif self.unit == "million":
            val = self.price / self.area
            return f"~{val:.1f} tr/m²"
        return ""

    @property
    def formatted_area(self) -> str:
        if self.area <= 0:
            return "Chưa cập nhật"
        if self.area == int(self.area):
            return f"{int(self.area)} m²"
        return f"{self.area:.1f}".rstrip("0").rstrip(".") + " m²"

    @property
    def category_label(self) -> str:
        return CATEGORY_LABELS.get(self.category, self.category or "Bất động sản")

    @property
    def transaction_label(self) -> str:
        return TRANSACTION_LABELS.get(self.transaction_type, "Bán")

    @property
    def legal_label(self) -> str:
        return LEGAL_LABELS.get(self.legal, self.legal or "Đang cập nhật")

    @property
    def ward_label(self) -> str:
        return WARD_LABELS.get(self.ward, self.ward or "Đà Lạt")

    @property
    def ward_short(self) -> str:
        label = self.ward_label
        if "(" in label:
            return label.split("(")[0].strip()
        return label

    @property
    def building_line_label(self) -> str:
        return BUILDING_LINE_LABELS.get(self.building_line, self.building_line or "Đang cập nhật")

    @property
    def furniture_label(self) -> str:
        return FURNITURE_LABELS.get(self.furniture, self.furniture or "Đang cập nhật")

    @property
    def status_label(self) -> str:
        return STATUS_LABELS.get(self.status, self.status)

    @property
    def street_display(self) -> str:
        if not self.street:
            return "Đường nội bộ"
        return self.street.strip().title()

    @property
    def display_title(self) -> str:
        trans = self.transaction_label
        cat = self.category_label
        street = self.street_display
        ward = self.ward_short
        return f"{trans} {cat} {street}, {ward}"

    @property
    def display_address(self) -> str:
        parts = []
        if self.street:
            parts.append(self.street_display)
        if self.ward:
            parts.append(self.ward_label)
        parts.append("Đà Lạt, Lâm Đồng")
        return ", ".join(parts)

    @property
    def structure_display(self) -> str:
        if self.structure <= 0:
            return ""
        if self.structure == int(self.structure):
            return f"{int(self.structure)} tầng"
        return f"{self.structure} tầng"

    @property
    def primary_image(self) -> str:
        if self.images and len(self.images) > 0:
            return self.images[0]
        return "/static/images/placeholder.svg"

    @property
    def image_count(self) -> int:
        return len(self.images)

    @property
    def description_paragraphs(self) -> List[str]:
        if not self.description:
            return []
        lines = [line.strip() for line in self.description.splitlines() if line.strip()]
        return lines

    @classmethod
    def from_row(cls, row) -> "RealEstateProduct":
        return cls(
            id=str(row["id"]),
            pid=str(row["pid"] or ""),
            status=str(row["status"] or "selling"),
            transaction_type=str(row["transaction_type"] or "sale"),
            province=str(row["province"] or "lam_dong"),
            district=str(row["district"] or "da_lat"),
            ward=str(row["ward"] or ""),
            street=str(row["street"] or ""),
            phone_number=str(row["phone_number"] or ""),
            category=str(row["category"] or ""),
            area=float(row["area"] or 0.0),
            price=float(row["price"] or 0.0),
            unit=str(row["unit"] or "billion"),
            legal=str(row["legal"] or ""),
            structure=float(row["structure"] or 0.0),
            function=str(row["function"] or ""),
            building_line=str(row["building_line"] or ""),
            furniture=str(row["furniture"] or ""),
            description=str(row["description"] or ""),
            created_at=str(row["created_at"] or ""),
            updated_at=str(row["updated_at"] or ""),
            images=[]
        )
