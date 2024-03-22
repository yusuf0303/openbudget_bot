from aiogram import types

from loader import dp
from states.user import USER


# Echo bot
@dp.message_handler(state=USER.payment)
async def bot_echo(message: types.Message):
    await message.answer("Ovoz berishda davom etish uchun pastdagi 'Menyuga qaytish 🔝' tugamsini bosing 👇")
