from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_a"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_a"),
    ]]
)
