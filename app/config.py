import os
import json
from dotenv import load_dotenv

load_dotenv()

# Thư mục gốc của project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_JSON_PATH = os.path.join(ROOT_DIR, "settings.json")

class Config:
    def __init__(self):
        json_data = {}
        self.source = ".env"
        
        # 1. Đọc từ settings.json nếu file này tồn tại
        if os.path.isfile(SETTINGS_JSON_PATH):
            try:
                with open(SETTINGS_JSON_PATH, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                    self.source = "settings.json"
            except Exception as e:
                print(f"[CẢNH BÁO] Không thể phân tích cú pháp settings.json: {e}")

        # 2. Ưu tiên: settings.json > .env / OS env > default
        raw_db = json_data.get("db_path") or os.getenv("DB_PATH", "./products.db")
        self.DB_PATH = os.path.abspath(os.path.expanduser(str(raw_db).strip('"\'')))

        raw_images = json_data.get("images_dir") or os.getenv("IMAGES_DIR", "./images")
        self.IMAGES_DIR = os.path.abspath(os.path.expanduser(str(raw_images).strip('"\'')))

        self.PORT = int(json_data.get("port") or os.getenv("PORT", 8000))
        self.HOST = str(json_data.get("host") or os.getenv("HOST", "0.0.0.0"))
        self.CONTACT_PHONE = str(json_data.get("contact_phone") or os.getenv("CONTACT_PHONE", "")).strip('"\'')
        self.CONTACT_ZALO = str(json_data.get("contact_zalo") or os.getenv("CONTACT_ZALO", "")).strip('"\'')
        self.SITE_NAME = str(json_data.get("site_name") or os.getenv("SITE_NAME", "Bất Động Sản Đà Lạt")).strip('"\'')

        prefer_wm = json_data.get("prefer_watermark")
        if prefer_wm is None:
            prefer_wm = os.getenv("PREFER_WATERMARK", "true")
        self.PREFER_WATERMARK = str(prefer_wm).lower() in ("true", "1", "yes")

        # Gemini API Key: settings.json -> .env -> OS ENV -> sibling my-manager.v1/.env
        api_key = json_data.get("gemini_api_key") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            sibling_env = os.path.abspath(os.path.join(ROOT_DIR, "..", "my-manager.v1", ".env"))
            if os.path.isfile(sibling_env):
                try:
                    with open(sibling_env, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip().startswith("GEMINI_API_KEY="):
                                val = line.strip().split("=", 1)[1].strip("\"' ")
                                if val:
                                    api_key = val
                                    break
                except Exception:
                    pass
        self.GEMINI_API_KEY = str(api_key or "").strip("\"' ")

config = Config()
