from aiogram.dispatcher.filters.state import StatesGroup, State


class CheckoutState(StatesGroup):
    check_cart = State()
    name = State()
    when_bday = State()
    address = State()
    cash_or_online = State()
    phone = State()
    location = State()
    when_to_go = State()
    name_person_bday = State()
    kimning_nomidan = State()
    bizni_kutibol = State()
    confirm = State()
