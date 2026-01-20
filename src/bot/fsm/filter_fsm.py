from aiogram.fsm.state import State, StatesGroup

class FilterStates(StatesGroup):
    waiting_for_make = State()
    waiting_for_model = State()
    waiting_for_min_price = State()
    waiting_for_max_price = State()
    viewing_filters = State()
    confirming_delete = State()
