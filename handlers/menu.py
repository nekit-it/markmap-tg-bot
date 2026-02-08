from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from keyboards import main_menu_keyboard
from states import CreateMap
from services.storage import get_last_map # Убедись, что эта функция есть в storage.py

router = Router()

def get_menu_for_user(user_id: int):
    """Вспомогательная функция для получения клавиатуры с актуальной ссылкой"""
    last_map = get_last_map(user_id)
    url = last_map['url'] if last_map else None
    return main_menu_keyboard(last_map_url=url)

@router.message(Command("menu"))
async def menu_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Главное меню:",
        reply_markup=get_menu_for_user(message.from_user.id)
    )

@router.message()
async def main_menu_handler(message: Message, state: FSMContext):
    text = message.text

    if text == "📄 Создать карту":
        await message.answer(
            "Загрузи файл или фото документа.",
            reply_markup=None # Убираем клавиатуру, чтобы не мешала
        )
        await state.set_state(CreateMap.waiting_for_file)
        return

    if text == "📚 История":
        # Логика истории в handlers/history.py, здесь можно просто перенаправить
        # Но aiogram так просто не перенаправляет message, поэтому лучше пусть user нажмет кнопку,
        # либо импортировать handler. 
        # Т.к. у тебя отдельный handler на текст "📚 История", этот блок может и не сработать, 
        # если роутеры подключены в правильном порядке.
        # Оставим pass, чтобы сработал handlers/history.py
        pass 

    # Если текст не распознан, просто показываем меню снова
    # (но с защитой, чтобы не спамить в ответ на любое сообщение)
    # await message.answer("Главное меню:", reply_markup=get_menu_for_user(message.from_user.id))