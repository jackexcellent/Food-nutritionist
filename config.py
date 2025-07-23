import os
from dotenv import load_dotenv

load_dotenv()  # 自動從 .env 或 test.env 載入，不需手動判斷

DISCORD_BOT_API_KEY = os.getenv("DISCORD_BOT_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


if not DISCORD_BOT_API_KEY:
    raise ValueError("請在 .env 設定 DISCORD_BOT_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("請在 .env 設定 GEMINI_API_KEY")