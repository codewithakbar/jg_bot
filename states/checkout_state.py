from aiogram.dispatcher.filters.state import StatesGroup, State


class CheckoutState(StatesGroup):
    check_cart = State()
    name = State()
    address = State()
    phone = State()
    location = State()
    confirm = State()
