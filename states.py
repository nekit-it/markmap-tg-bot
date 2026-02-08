from aiogram.fsm.state import StatesGroup, State

class CreateMap(StatesGroup):
    waiting_for_file = State()
    waiting_for_title = State()
    waiting_for_depth = State()
    waiting_for_llm = State()
    processing = State()

class Global(StatesGroup):
    idle = State()
