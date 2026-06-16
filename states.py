from aiogram.fsm.state import State, StatesGroup


class Code(StatesGroup):
    wait = State()
