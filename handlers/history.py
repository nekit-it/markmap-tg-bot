from aiogram import Router
from aiogram.types import Message

from services.storage import get_user_maps
from keyboards import history_keyboard

router = Router()

@router.message(lambda m: m.text == "📚 История")
async def history_handler(message: Message):
    maps = get_user_maps(message.from_user.id)

    if not maps:
        await message.answer("История пуста.")
        return

    await message.answer(
        "📚 Твои карты:",
        reply_markup=history_keyboard(maps)
    )
