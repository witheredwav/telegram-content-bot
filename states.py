from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
waiting_for_code = State()

class AdminStates(StatesGroup):
waiting_for_content = State()
