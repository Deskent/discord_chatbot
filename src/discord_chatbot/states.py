"""FSM states"""

from aiogram.dispatcher.filters.state import State, StatesGroup


class UserStates(StatesGroup):

    frequency_post = State()
    in_work = State()
    normal_start = State()
    parsed_start = State()
    parsing = State()
    set_pause = State()
