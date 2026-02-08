# from aiogram.types import (
#     ReplyKeyboardMarkup,
#     KeyboardButton,
#     InlineKeyboardMarkup,
#     InlineKeyboardButton,
#     WebAppInfo
# )
# from config import NETLIFY_URL
# from config import YC_WEBSITE_HOST

# # --- Главное меню ---

# def main_menu_keyboard(last_map_url: str = None):
#     """
#     Генерирует меню. Если есть last_map_url, кнопка ведет на карту.
#     Если нет — на главную страницу (index.html).
#     """
#     # Если URL не передан, ведем на корень (заглушку)
#     #target_url = last_map_url if last_map_url else f"https://{YC_WEBSITE_HOST}/index.html"
#     target_url = last_map_url if last_map_url else YC_WEBSITE_HOST

#     return ReplyKeyboardMarkup(
#         keyboard=[
#             [KeyboardButton(text="📄 Создать карту")],
#             [KeyboardButton(text="📚 История")],
#             [
#                 KeyboardButton(
#                     text="🌐 Открыть мини-приложение",
#                     web_app=WebAppInfo(url=target_url)
#                 )
#             ]
#         ],
#         resize_keyboard=True,
#     )

# # --- Клавиатуры процесса ---

# def depth_keyboard():
#     return ReplyKeyboardMarkup(
#         keyboard=[
#             [KeyboardButton(text="Кратко")],
#             [KeyboardButton(text="Средне")],
#             [KeyboardButton(text="Подробно")],
#         ],
#         resize_keyboard=True,
#     )

# def llm_keyboard():
#     return ReplyKeyboardMarkup(
#         keyboard=[
#             [KeyboardButton(text="Авто")],
#         ],
#         resize_keyboard=True,
#     )

# def history_keyboard(maps: list):
#     keyboard = []
#     for m in maps:
#         # Кнопка открытия сразу в Mini App
#         url = m.get('url')
#         buttons = []
        
#         # Если есть URL, добавляем кнопку WebApp
#         if url:
#              buttons.append(
#                 InlineKeyboardButton(
#                     text=f"🌐 {m['title']}",
#                     web_app=WebAppInfo(url=url)
#                 )
#              )
        
#         # Кнопка для получения текста в чат
#         buttons.append(
#             InlineKeyboardButton(
#                 text="👁 Текст",
#                 callback_data=f"open_map:{m['id']}",
#             )
#         )
#         keyboard.append(buttons)

#     return InlineKeyboardMarkup(inline_keyboard=keyboard)

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)
from config import YC_WEBSITE_HOST

# --- Вспомогательная функция для очистки URL ---
def get_clean_webapp_url(url: str = None) -> str:
    """Гарантирует, что ссылка начинается с https:// и содержит правильный хост."""
    clean_host = YC_WEBSITE_HOST.replace("https://", "").replace("http://", "").strip("/")
    
    if not url or "http" not in url:
        # Если ссылки нет, возвращаем главную страницу бакета
        return f"https://{clean_host}/index.html"
    
    # Если ссылка есть, принудительно меняем http на https
    if url.startswith("http://"):
        return url.replace("http://", "https://", 1)
    
    return url

# --- Главное меню ---

def main_menu_keyboard(last_map_url: str = None):
    """
    Генерирует меню. Использует HTTPS для Mini App.
    """
    target_url = get_clean_webapp_url(last_map_url)

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📄 Создать карту")],
            [KeyboardButton(text="📚 История")],
            [
                KeyboardButton(
                    text="🌐 Открыть мини-приложение",
                    web_app=WebAppInfo(url=target_url)
                )
            ]
        ],
        resize_keyboard=True,
    )

# --- Клавиатуры процесса ---

def depth_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Кратко")],
            [KeyboardButton(text="Средне")],
            [KeyboardButton(text="Подробно")],
        ],
        resize_keyboard=True,
    )

def llm_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Авто")],
        ],
        resize_keyboard=True,
    )

def history_keyboard(maps: list):
    keyboard = []
    for m in maps:
        url = m.get('url')
        buttons = []
        
        if url:
            # Исправляем протокол на https на лету для кнопок истории
            safe_url = get_clean_webapp_url(url)
            buttons.append(
                InlineKeyboardButton(
                    text=f"🌐 {m['title']}",
                    web_app=WebAppInfo(url=safe_url)
                )
            )
        
        buttons.append(
            InlineKeyboardButton(
                text="👁 Текст",
                callback_data=f"open_map:{m['id']}",
            )
        )
        keyboard.append(buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)