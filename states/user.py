from aiogram.dispatcher.filters.state import StatesGroup, State


class USER(StatesGroup):
    phone_number = State()
    payment = State()
    phone_number_call = State()
    voted = State()
    verified = State()
    failed = State()
