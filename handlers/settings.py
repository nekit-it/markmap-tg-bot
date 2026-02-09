from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from uuid import uuid4

from states import CreateMap
from keyboards import depth_keyboard, llm_keyboard, main_menu_keyboard
from services.storage import save_map
from services.yandex_storage import upload_html_to_s3

router = Router()

@router.message(CreateMap.waiting_for_title)
async def title_handler(message: Message, state: FSMContext):
    # Получаем данные сразу, чтобы проверить is_html
    data = await state.get_data()
    
    # Если пользователь нажал кнопку авто-названия, сохраняем None
    if message.text == "🤖 Оставить на выбор ИИ":
        if data.get("is_html"):
            # Для HTML авто-название = имя файла
            await state.update_data(user_title=data.get("source_message").document.file_name)
        else:
            await state.update_data(user_title=None)
    else:
        await state.update_data(user_title=message.text)
        
    # --- БЛОК ОБРАБОТКИ HTML (НОВЫЙ) ---
    if data.get("is_html"):
        status_message = await message.answer("☁️ Загружаю HTML карту...")
        try:
            source_message = data.get("source_message")
            
            # Скачивание файла
            file_info = await message.bot.get_file(source_message.document.file_id)
            file_bytes = await message.bot.download_file(file_info.file_path)
            content = file_bytes.read()
            
            # Загрузка в S3
            filename = f"{uuid4()}.html"
            public_url = upload_html_to_s3(content, filename)
            
            # Определяем финальное название
            current_data = await state.get_data()
            final_title = current_data.get("user_title") or source_message.document.file_name

            # Сохранение в базу
            save_map(
                user_id=message.from_user.id,
                title=final_title,
                depth="HTML Импорт",
                structure=[],
                markmap="",
                url=public_url,
            )

            await status_message.delete()

            # Кнопка для конкретной карты
            inline_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Открыть карту", web_app=WebAppInfo(url=public_url))]
            ])

            await message.answer(
                f"✅ <b>Карта готова: {final_title}</b>",
                reply_markup=inline_kb,
                parse_mode="HTML"
            )

            await state.clear()
            # В главное меню
            await message.answer(
                "Возврат в меню:",
                reply_markup=main_menu_keyboard(last_map_url=public_url)
            )
        except Exception as e:
            await status_message.edit_text(f"❌ Ошибка при загрузке: {e}")
            
        return

    await message.answer("Выбери глубину анализа\n\nКратко: только ключевые идеи\nСредне: сбалансированная, с основными пунктами\nПодробно: подробная карта", reply_markup=depth_keyboard())
    await state.set_state(CreateMap.waiting_for_depth)

@router.message(CreateMap.waiting_for_depth)
async def depth_handler(message: Message, state: FSMContext):
    await state.update_data(depth=message.text)
    await message.answer("Выбери модель LLM:", reply_markup=llm_keyboard())
    await state.set_state(CreateMap.waiting_for_llm)
