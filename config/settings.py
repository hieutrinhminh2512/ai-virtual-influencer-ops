import os
import sys
from pathlib import Path
from dotenv import load_dotenv

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    def __init__(self):
        self.GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
        self.TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
        self.YOUTUBE_CLIENT_SECRET_FILE: str = os.getenv("YOUTUBE_CLIENT_SECRET_FILE", "client_secret.json")
        self.YOUTUBE_PRIVACY_STATUS: str = os.getenv("YOUTUBE_PRIVACY_STATUS", "private")
        
        self.PORT: int = int(os.getenv("PORT", 8000))
        self.HOST: str = os.getenv("HOST", "127.0.0.1")
        self.BROWSER_USER_DATA_DIR: str = os.getenv("BROWSER_USER_DATA_DIR", "./browser_profile")
        self.HEADLESS_BROWSER: bool = os.getenv("HEADLESS_BROWSER", "false").lower() == "true"
        self.GOOGLE_FLOW_URL: str = os.getenv("GOOGLE_FLOW_URL", "https://labs.google/fx/tools/flow")
        
        self.BASE_DIR: Path = BASE_DIR
        self.OUTPUTS_DIR: Path = BASE_DIR / "outputs"
        self.SCRIPTS_DIR: Path = BASE_DIR / "outputs" / "scripts"
        self.VIDEOS_DIR: Path = BASE_DIR / "outputs" / "videos"
        self.TEMP_DIR: Path = BASE_DIR / "outputs" / "temp"

        # Ensure directories exist
        for p in [self.OUTPUTS_DIR, self.SCRIPTS_DIR, self.VIDEOS_DIR, self.TEMP_DIR]:
            p.mkdir(parents=True, exist_ok=True)

settings = Settings()
