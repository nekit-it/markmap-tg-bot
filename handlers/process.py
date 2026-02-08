from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from uuid import uuid4

from states import CreateMap
from services.llm import generate_markmap
# from services.github_storage import upload_to_github 
from keyboards import main_menu_keyboard
from services.storage import save_map, upload_to_s3 
from services.document_text import extract_text
from config import YC_WEBSITE_HOST 

router = Router()

@router.message(CreateMap.waiting_for_llm)
async def process_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    depth = data.get("depth", "Средняя")
    source_message = data.get("source_message")

    status_message = await message.answer("🧠 Анализирую документ...")

    text = await extract_text(source_message)
    try:
        await status_message.edit_text("🗺 Формирую структуру...")
    except Exception:
        pass

    # Генерация контента
    result = generate_markmap(text=text, depth=depth)
    
    # Генерируем уникальное имя файла
    filename = f"{uuid4()}.md"

    # public_url = None
    # try:
    #     await status_message.edit_text("☁️ Сохраняю...")
    #     public_url = upload_to_github(result["markmap"], filename)
    # except Exception as e:
    #     print(f"Github Upload Error: {e}")
    #     await message.answer(f"⚠️ Ошибка сохранения в облако: {e}")
    # --------------------------------------------

    # --- НОВЫЙ БЛОК S3 ---
    # --- ПОЛНОСТЬЮ ИСПРАВЛЕННЫЙ БЛОК S3 ---
    try:
        await status_message.edit_text("☁️ Сохраняю в S3...")
        
        # Получаем путь (например: generated_maps/uuid.md)
        s3_path = upload_to_s3(result["markmap"], filename)
        
        # ОЧИСТКА ХОСТА: убираем http/https и лишние слэши
        clean_host = YC_WEBSITE_HOST.replace("https://", "").replace("http://", "").strip("/")
        
        # ОЧИСТКА ПУТИ: если s3_path вдруг вернул полную ссылку, берем только хвост
        if "file=" in s3_path:
            s3_path = s3_path.split("file=")[-1]
        elif "http" in s3_path:
            s3_path = s3_path.split("/")[-1]
            s3_path = f"generated_maps/{s3_path}"

        app_url = f"https://{clean_host}/index.html?file={s3_path}"
        
    except Exception as e:
        print(f"S3 Error: {e}")
        await message.answer(f"❌ Ошибка S3: {e}")
        await state.clear()
        return
  
    save_map(
        user_id=message.from_user.id,
        title=result["title"],
        depth=depth,
        structure=result["nodes"],
        markmap=result["markmap"],
        url=app_url, 
    )

    try:
        await status_message.delete()
    except Exception:
        pass

    # Кнопка для конкретной карты
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Открыть карту", web_app=WebAppInfo(url=app_url))]
    ])

    await message.answer(
        f"✅ <b>Карта готова: {result['title']}</b>\n\n"
        f"<code>{result['markmap']}</code>",
        reply_markup=inline_kb,
        parse_mode="HTML"
    )

    await state.clear()
    # В главное меню
    await message.answer(
        "Возврат в меню:",
        reply_markup=main_menu_keyboard(last_map_url=app_url)
    )