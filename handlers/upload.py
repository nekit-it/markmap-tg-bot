from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import CreateMap
from keyboards import auto_title_keyboard

router = Router()

@router.message(CreateMap.waiting_for_file)
async def upload_handler(message: Message, state: FSMContext):
    if not message.document and not message.photo:
        await message.answer("Пожалуйста, загрузи файл или фото.")
        return

    # Проверяем, является ли файл HTML
    is_html = False
    if message.document and message.document.file_name:
        fname = message.document.file_name.lower()
        if fname.endswith('.html') or fname.endswith('.htm'):
            is_html = True

    # Сохраняем исходное сообщение и флаг HTML
    await state.update_data(source_message=message, is_html=is_html)

    # Логика ответа пользователю
    if is_html:
        await message.answer(
            "Вижу HTML файл. Как назовем карту? Введи название или нажми кнопку, чтобы оставить имя файла.",
            reply_markup=auto_title_keyboard() # Можно использовать ту же кнопку "Оставить..."
        )
    else:
        await message.answer(
            "Файл принят. Введи название для карты или нажми на кнопку ниже, чтобы ИИ придумал его сам.",
            reply_markup=auto_title_keyboard()
        )
        
    await state.set_state(CreateMap.waiting_for_title)
