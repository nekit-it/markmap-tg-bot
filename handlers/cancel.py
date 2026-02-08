from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from services.storage import get_last_map
from keyboards import main_menu_keyboard

router = Router()

@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    
    last_map = get_last_map(message.from_user.id)
    url = last_map['url'] if last_map else None

    await message.answer(
        "Сценарий отменён.",
        reply_markup=main_menu_keyboard(last_map_url=url)
    )