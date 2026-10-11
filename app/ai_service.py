# app/ai_service.py
import re
import random
import httpx
from typing import Dict, List, Optional, Tuple, Any
from app.config import config

REAL_ESTATE_ANGLES: List[Dict[str, str]] = [
    {
        "name": "Thực tế & Súc tích",
        "description": "Đi thẳng vào thông số cốt lõi (vị trí, diện tích, công năng, giá), không văn vẻ rườm rà."
    },
    {
        "name": "Trải nghiệm sống & Tiện ích",
        "description": "Nêu bật không gian sống thoáng đãng, thuận tiện đi lại, gần trường, chợ, siêu thị."
    },
    {
        "name": "Góc nhìn giá trị & Tiềm năng",
        "description": "Sắc bén, nhấn mạnh vị trí đẹp, tính thanh khoản cao, phù hợp ở hoặc khai thác cho thuê."
    },
    {
        "name": "Gợi mở nhu cầu",
        "description": "Mở đầu tự nhiên bằng gợi ý tìm nhà an cư hoặc giữ tài sản hợp lý trong tầm tài chính."
    },
    {
        "name": "Review chân thực",
        "description": "Khách quan, gần gũi như người đi xem nhà thực tế chia sẻ lại các điểm cộng lớn."
    }
]

FORBIDDEN_CLICHES: List[str] = [
    # Từ sáo rỗng & giật gân
    "siêu phẩm", "cực phẩm", "cơ hội vàng", "đẹp lung linh", "đẹp ngỡ ngàng",
    "không thể bỏ qua", "nhanh tay kẻo lỡ", "hoa hậu", "ngọc trinh", "hàng hiếm",
    "đỉnh cao", "rẻ tụt quần", "rẻ sập sàn", "rẻ nhất quả đất", "sốc", "khủng",
    # Từ vi phạm chính sách tài chính / BĐS tiêu cực (dễ bị shadowban/spam flag)
    "vỡ nợ", "cắt lỗ", "bán tháo", "ngộp thở", "ngộp ngân hàng", "phát mãi",
    "túng tiền", "cam kết sinh lời", "bao lời", "lời gấp đôi",
    # Từ nhạy cảm & engagement bait
    "chính chủ", "chia sẻ ngay", "tag bạn bè", "thả tim", "chấm bài"
]

RANDOM_ICONS_POOL: List[str] = [
    "🏡", "📍", "🌿", "🔑", "✨", "📌", "☀️", "🏷️", "🏢", "🛋️", "📐", "🚗", "🌳", "🪴"
]


class AIPromptHelper:
    """
    Helper tạo prompt chuẩn SEO Facebook, tuân thủ chính sách Meta và bóc tách kết quả từ Gemini AI.
    Kế thừa 100% logic từ my-manager.v1.
    """

    @staticmethod
    def get_angles() -> List[Dict[str, str]]:
        return REAL_ESTATE_ANGLES

    @staticmethod
    def build_real_estate_rewrite_prompt(
        raw_title: str,
        raw_desc: str,
        is_rental: Optional[bool] = None,
        angle_name: Optional[str] = None,
        contact_phone: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Tạo prompt tối ưu hóa cho bài đăng Facebook BĐS.
        Trả về: (prompt, angle_used_name)
        """
        # Chọn góc nhìn
        selected_angle = None
        if angle_name:
            for a in REAL_ESTATE_ANGLES:
                if a["name"].lower() == angle_name.lower():
                    selected_angle = a
                    break
        if not selected_angle:
            selected_angle = random.choice(REAL_ESTATE_ANGLES)

        cliches_sample = ", ".join([f'"{c}"' for c in random.sample(FORBIDDEN_CLICHES, min(6, len(FORBIDDEN_CLICHES)))])
        sample_icons = " ".join(random.sample(RANDOM_ICONS_POOL, min(3, len(RANDOM_ICONS_POOL))))

        phone = contact_phone or config.CONTACT_PHONE or "0375 155 525"

        if is_rental is True:
            rental_rule = "- QUY ĐỊNH PHÁP LÝ (BẮT BUỘC): Đây là bài đăng CHO THUÊ BĐS. TUYỆT ĐỐI KHÔNG nhắc đến bất kỳ vấn đề pháp lý mua bán hay quyền sở hữu nào (như: mua bán vi bằng, sổ riêng xây dựng, sổ hồng, sổ đỏ, công chứng sang tên, đất thổ cư, quy hoạch...). Chỉ tập trung vào công năng, nội thất, tiện ích sinh hoạt, vị trí và giá thuê."
            contact_rule = f'4. Kêu gọi liên hệ (BẮT BUỘC): Luôn có thông tin liên hệ gồm SĐT: "LH: {phone} (zalo, hotline)".'
        elif is_rental is False:
            rental_rule = "- QUY ĐỊNH PHÁP LÝ (BẮT BUỘC): Nếu sản phẩm/bài đăng là dạng CHO THUÊ, TUYỆT ĐỐI KHÔNG nhắc đến bất kỳ vấn đề pháp lý mua bán hay quyền sở hữu nào. Với BĐS bán, nêu rõ pháp lý sổ sách minh bạch, rõ ràng."
            contact_rule = f'4. Kêu gọi liên hệ (BẮT BUỘC): Luôn có thông tin liên hệ gồm SĐT: "LH: {phone} (zalo, hotline)".'
        else:
            rental_rule = "- QUY ĐỊNH PHÁP LÝ (BẮT BUỘC): Nếu sản phẩm/bài đăng là dạng CHO THUÊ, TUYỆT ĐỐI KHÔNG nhắc đến bất kỳ vấn đề pháp lý mua bán hay quyền sở hữu nào."
            contact_rule = f'4. Kêu gọi liên hệ (BẮT BUỘC): Luôn có thông tin liên hệ gồm SĐT: "LH: {phone} (zalo, hotline)".'

        prompt = f"""Bạn là chuyên gia viết bài BĐS chuẩn SEO Facebook, tuân thủ nghiêm ngặt chính sách và thuật toán chống spam của Meta.

Nhiệm vụ: Viết lại tin BĐS sau thành bài đăng Facebook NGẮN GỌN, TỰ NHIÊN, DỄ ĐỌC.
Góc nhìn thể hiện: {selected_angle['name']} ({selected_angle['description']}).

TIÊU CHUẨN NỘI DUNG & SEO FACEBOOK:
1. Độ dài & Bố cục: Ngắn gọn (dưới 100 từ), 3-5 dòng/gạch đầu dòng ngắt quãng thoáng mắt, tối ưu hiển thị trên điện thoại.
2. Chuẩn SEO Facebook: Dòng đầu nêu rõ [Loại BĐS] + [Vị trí/Quận/Đường] + Điểm sáng chính để tối ưu tìm kiếm trên Facebook.
3. Thân bài: Đi thẳng vào thông tin người mua/thuê cần (diện tích, kết cấu, tiện ích nổi bật, giá bán/thuê). Giữ đúng thông số gốc, bỏ mục trống/0/mã tin/PID.
{contact_rule}
5. Cuối bài: Kèm đúng 3-4 hashtag chuẩn SEO (ví dụ: #nhadep #bds_khuvuc #muabannhadat hoặc #chothuenha).

CHỐNG SPAM & TUÂN THỦ CHÍNH SÁCH FACEBOOK:
- CẤM TỪ SÁO RỖNG & GIẬT TÍT: Không dùng {cliches_sample}.
- CẤM TỪ TIÊU CỰC / VI PHẠM TÀI CHÍNH: Tuyệt đối không dùng "vỡ nợ", "cắt lỗ", "bán tháo", "ngộp", "phát mãi", "cam kết lời".
- CẤM MỒI TƯƠNG TÁC (Engagement Bait): Không dùng "chia sẻ ngay", "tag bạn bè", "thả tim", "chấm bài".
- CẤM ĐỊNH DẠNG SPAM: Không dùng markdown (**), không viết hoa toàn bộ (ALL CAPS), chỉ dùng 2-3 icon nhẹ nhàng ({sample_icons}).
{rental_rule}

BẮT BUỘC TRẢ VỀ THEO CẤU TRÚC (ngăn cách chính xác bằng dòng '===SPLIT===', không thêm lời dẫn hay giải thích):
Tiêu đề mới (dưới 85 ký tự, chuẩn SEO)
===SPLIT===
Nội dung mô tả mới (bao gồm thông tin bất động sản, liên hệ / số điện thoại và hashtag)

Tiêu đề gốc: {raw_title}
Mô tả gốc: {raw_desc}"""

        return prompt.strip(), selected_angle["name"]

    @staticmethod
    def parse_real_estate_rewrite_response(
        response: str,
        default_title: str = "",
        default_desc: str = ""
    ) -> Tuple[str, str]:
        """
        Bóc tách chính xác tiêu đề và mô tả từ kết quả Gemini, hỗ trợ phân tách '===SPLIT==='.
        """
        if not response or not response.strip():
            return default_title, default_desc

        clean_text = response.strip()

        def _clean_part(part: str, is_title: bool = False) -> str:
            p = part.strip()
            # Bỏ markdown code blocks nếu có
            p = re.sub(r"^```[a-zA-Z]*\n?", "", p)
            p = re.sub(r"\n?```$", "", p)
            p = p.strip()

            # Bỏ dấu nháy kép bọc quanh nếu có
            if (p.startswith('"') and p.endswith('"')) or (p.startswith("'") and p.endswith("'")):
                p = p[1:-1].strip()
            if p.startswith("[") and p.endswith("]"):
                p = p[1:-1].strip()

            if is_title:
                # Xóa các nhãn tiêu đề thừa
                p = re.sub(r"^(?:tiêu\s*đề(?:\s*mới)?|title)\s*[:：\-]\s*", "", p, flags=re.IGNORECASE)
                if p.startswith("[") and p.endswith("]"):
                    p = p[1:-1].strip()
                p = re.sub(r"^#+\s*", "", p)
            else:
                p = re.sub(r"^(?:mô\s*tả(?:\s*mới)?|description|nội\s*dung(?:\s*mới)?)\s*[:：\-]\s*", "", p, flags=re.IGNORECASE)
                if p.startswith("[") and p.endswith("]"):
                    p = p[1:-1].strip()

            # Xóa dấu sao markdown **text** -> text
            p = re.sub(r"\*\*(.*?)\*\*", r"\1", p)
            p = re.sub(r"\*(.*?)\*", r"\1", p)
            return p.strip()

        # 1. Tìm phân tách ===SPLIT===
        split_match = re.search(r'(?:^|\n)\s*[\*=_#-]*\s*SPLIT\s*[\*=_#-]*\s*(?:\n|$)', clean_text, re.IGNORECASE)
        if split_match:
            title_part = clean_text[:split_match.start()]
            desc_part = clean_text[split_match.end():]
            title = _clean_part(title_part, is_title=True)
            desc = _clean_part(desc_part, is_title=False)
            return title or default_title, desc or default_desc

        # 2. Tìm dạng nhãn Tiêu đề / Mô tả
        label_match = re.search(
            r'(?:^|\n)\s*(?:tiêu\s*đề(?:\s*mới)?|title)\s*[:：\-]\s*(.*?)\n+\s*(?:mô\s*tả(?:\s*mới)?|description|nội\s*dung(?:\s*mới)?)\s*[:：\-]\s*(.*)',
            clean_text,
            re.DOTALL | re.IGNORECASE
        )
        if label_match:
            title = _clean_part(label_match.group(1), is_title=True)
            desc = _clean_part(label_match.group(2), is_title=False)
            return title or default_title, desc or default_desc

        # 3. Phân tách theo dòng đầu tiên nếu dòng đầu ngắn (< 120 ký tự)
        lines = [line.strip() for line in clean_text.splitlines() if line.strip()]
        if len(lines) >= 2 and len(lines[0]) <= 120:
            title = _clean_part(lines[0], is_title=True)
            desc_raw = clean_text[clean_text.find(lines[0]) + len(lines[0]):].strip()
            desc = _clean_part(desc_raw, is_title=False)
            return title or default_title, desc or default_desc

        return default_title, _clean_part(clean_text, is_title=False)


class GeminiService:
    """
    Service gọi Google Gemini API trực tiếp bằng HTTP client bất đồng bộ.
    Hỗ trợ cơ chế tự động chuyển đổi mô hình (fallback) sang mô hình khả dụng.
    """

    CANDIDATE_MODELS = [
        "gemini-flash-lite-latest",
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash",
        "gemini-2.5-flash-lite"
    ]

    def __init__(self):
        self.api_key = config.GEMINI_API_KEY

    def _get_api_key(self) -> str:
        key = self.api_key or config.GEMINI_API_KEY
        if not key:
            raise ValueError("GEMINI_API_KEY chưa được cấu hình trong settings.json hoặc file .env.")
        return key

    async def rewrite_text(self, prompt: str) -> str:
        api_key = self._get_api_key()

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.85,
                "topP": 0.95,
                "topK": 40
            }
        }

        last_error = None
        async with httpx.AsyncClient() as client:
            for model in self.CANDIDATE_MODELS:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                try:
                    response = await client.post(url, json=payload, timeout=25.0)
                    if response.status_code == 200:
                        data = response.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text", "").strip()
                    else:
                        last_error = f"Model {model} returned HTTP {response.status_code}: {response.text[:200]}"
                except Exception as e:
                    last_error = f"Model {model} failed: {e}"
                    continue

        raise RuntimeError(f"Không thể gọi Gemini API: {last_error}")

    async def rewrite_real_estate(
        self,
        raw_title: str,
        raw_desc: str,
        is_rental: Optional[bool] = None,
        angle_name: Optional[str] = None,
        contact_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Viết lại toàn bộ tin BĐS thành Tiêu đề + Mô tả chuẩn SEO Facebook.
        """
        prompt, chosen_angle = AIPromptHelper.build_real_estate_rewrite_prompt(
            raw_title=raw_title,
            raw_desc=raw_desc,
            is_rental=is_rental,
            angle_name=angle_name,
            contact_phone=contact_phone
        )

        raw_response = await self.rewrite_text(prompt)
        rewritten_title, rewritten_desc = AIPromptHelper.parse_real_estate_rewrite_response(
            raw_response,
            default_title=raw_title,
            default_desc=raw_desc
        )

        return {
            "status": "success",
            "title": rewritten_title,
            "description": rewritten_desc,
            "angle": chosen_angle,
            "raw_response": raw_response
        }


gemini_service = GeminiService()
