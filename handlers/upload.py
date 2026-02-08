from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import CreateMap

router = Router()

@router.message(CreateMap.waiting_for_file)
async def upload_handler(message: Message, state: FSMContext):
    if not message.document and not message.photo:
        await message.answer("Пожалуйста, загрузи файл или фото.")
        return

    await state.update_data(source_message=message)

    await message.answer("Файл принят. Введи название карты.")
    await state.set_state(CreateMap.waiting_for_title)
