import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
YANDEX_MODEL = os.getenv("YANDEX_MODEL", "general")
YANDEX_OCR_URL = os.getenv("YANDEX_OCR_URL", "https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText")
YANDEX_URL = os.getenv('YANDEX_URL')
YANDEX_API_URL = os.getenv(
    "YANDEX_API_URL",
    "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
)
YC_ACCESS_KEY_ID = os.getenv("YC_ACCESS_KEY_ID")
YC_SECRET_ACCESS_KEY = os.getenv("YC_SECRET_ACCESS_KEY")
YC_BUCKET_NAME = os.getenv("YC_BUCKET_NAME", "webapp-tgmini") 
YC_S3_ENDPOINT = os.getenv("YC_S3_ENDPOINT", "https://storage.yandexcloud.net")
YC_WEBSITE_HOST = os.getenv(
    "YC_WEBSITE_HOST",
    "webapp-tgmini.website.yandexcloud.net",  
)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
NETLIFY_URL = os.getenv("NETLIFY_URL")  
GITHUB_REPO = os.getenv("GITHUB_REPO")  

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_DEFAULT_MODEL = os.getenv("OPENROUTER_DEFAULT_MODEL", "openai/gpt-4.1-mini")
