from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import CreateMap
from keyboards import depth_keyboard, llm_keyboard

router = Router()

@router.message(CreateMap.waiting_for_title)
async def title_handler(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Выбери глубину анализа:", reply_markup=depth_keyboard())
    await state.set_state(CreateMap.waiting_for_depth)

@router.message(CreateMap.waiting_for_depth)
async def depth_handler(message: Message, state: FSMContext):
    await state.update_data(depth=message.text)
    await message.answer("Выбери модель LLM:", reply_markup=llm_keyboard())
    await state.set_state(CreateMap.waiting_for_llm)
