import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart, Text

from keyboards.inline.voting_type import voting_type, checking_number
from loader import dp, bot

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from states.user import USER

from openbudget_bot.data.config import ADMINS

users_amount = []
users = {}

vote_btn = ReplyKeyboardMarkup(resize_keyboard=True)
vote = KeyboardButton(text="Ovoz berish 🗣️")
connect = KeyboardButton(text="Admin ☎️")
vote_btn.add(vote)

voted_btn = ReplyKeyboardMarkup(resize_keyboard=True)
voted_btn.add(vote).add(connect)


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f"Assalomu alaykum, {message.from_user.full_name}!\nBotga xush kelibsiz 🤗\n\n"
                         f"Ovoz berish uchun pastdagi ovoz berish tugmasini bosing 👇\nOvoz berib bo'lganizda har bir "
                         f"ovoz uchun 10.000 so'mdan pulni plastik kartangizga 💳 yoki telefon raqamingizga 📲 tushirib "
                         f"olishingiz mumkin",
                         reply_markup=vote_btn)


@dp.message_handler(Text(equals="Ovoz berish 🗣️"))
async def voting(message: types.Message):
    get_phone = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Raqamni ulashish 📱",
                                                                                    request_contact=True)]], )
    await message.answer(text="Ovoz berish uchun telefon raqamingizni '+998XXXXXXXXX' ko'rinishida kiriting ✍️ "
                              "yoki pastdagi 'Raqamni ulashish 📱' tugmasini bosing", reply_markup=get_phone)


@dp.message_handler(Text(equals="Admin ☎️"))
async def contacting(message: types.Message, state: FSMContext):
    # receiving_money = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
    #     [InlineKeyboardButton(text="Telefon raqamga ( Paynet )📱", callback_data='to_phone')],
    #     [InlineKeyboardButton(text="Plastik kartaga 💳", callback_data='to_card')]
    # ])
    canceling = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Menyuga qaytish 🔝")]])
    await message.answer(text=f"Assalomu alaykum, {message.from_user.full_name}!\nPullaringizni qanday qabul "
                              f"qilmoqchisiz? Telefon raqam yoki plastik kartangiz raqamini yozib qoldiring ✍️\n\n",
                         reply_markup=canceling)
    await USER.payment.set()


@dp.message_handler(Text(equals="Menyuga qaytish 🔝"), state=USER.payment)
async def cancel(message: types.Message, state: FSMContext):
    # pattern = r'^\+998\d{2}\d{3}\d{2}\d{2}$'
    # pattern_card = r'^\d{4}\s\d{4}\s\d{4}\s\d{4}$'
    # if re.match(pattern, message.text) or re.search(pattern_card, message.text):
    await message.answer(text="Ovoz berishda davom eting 🗣️", reply_markup=voted_btn)
    await state.finish()


@dp.message_handler(state=USER.payment)
async def get_your_money(message: types.Message, state: FSMContext):
    # this_user = users_amount.count(message.from_user.id)
    data = await state.get_data()
    phone_number = data.get("phone_number")
    paid = InlineKeyboardMarkup(row_width=1, inline_keyboard=[[InlineKeyboardButton(text="To'landi ✅",
                                                                                    callback_data='paid')]])
    pattern = r'^\+998\d{2}\d{3}\d{2}\d{2}$'
    pattern_card = r'^\d{4}\s\d{4}\s\d{4}\s\d{4}$'
    if re.match(pattern, message.text) or re.search(pattern_card, message.text):
        await message.answer(text="Pullar tez orada hisobingizga o'tkaziladi ✅\nOvoz berishda davom eting 👇",
                             reply_markup=vote_btn)
        for admin in ADMINS:
            await bot.send_message(chat_id=admin, text=f"To'lov 📱\n\nID: {message.from_user.id} 🆔\n"
                                                       f"Foydalanuvchi: {message.from_user.full_name}\n"
                                                       f"Foydalanuvchi nomi: @{message.from_user.username}\n"
                                                       f"Telefon raqam: {phone_number}\n\n"
                                                       f"To'lov uchun telefon raqam: {message.text}", reply_markup=paid)
            await state.finish()
    else:
        await message.answer(text=f"Raqamingizda xatolik bor! Tekshirib qayta kiriting 👇\n\n{message.text}")


@dp.message_handler(content_types=types.ContentTypes.CONTACT)
async def got_contact(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number
    await message.answer(text="Ovoz berish turini tanlang 👇", reply_markup=voting_type)
    await state.update_data(
        {"phone_number": phone_number}
    )


@dp.message_handler()
async def got_contact_(message: types.Message, state: FSMContext):
    pattern = r'^\+998\d{2}\d{3}\d{2}\d{2}$'
    if re.match(pattern=pattern, string=message.text):
        await message.answer(text="Ovoz berish turini tanlang 👇", reply_markup=voting_type)
        await state.update_data(
            {"phone_number": message.text}
        )
    else:
        await message.answer(text=f"Raqamingizda xatolik bor!\nTekshirib qayta kiriting: 👇\n{message.text}")


@dp.callback_query_handler()
async def vote_type(call: types.CallbackQuery, state: FSMContext):
    callback = call.data
    data = await state.get_data()
    phone_number = data.get("phone_number")
    user_id = call.message.text.split(' ')[3]

    if callback == "telegram":
        await call.answer("Telegram orqali ovoz berish")
    elif callback == "site":
        await call.answer("Site orqali ovoz berish")
    elif callback == "confirm":
        await call.message.delete()
        await call.answer("Iltimos kutib turing ⏳")
        await call.message.answer(text="Raqamingiz tekshirilmoqda! Bu bir necha soat vaqt olishi mumkin, ovozingiz "
                                       "tasdiqlanganda sizning hisobingizga pul o'tkaziladi!",
                                  reply_markup=vote_btn)
        sent_message = (f"Yangi ovoz 🗣️\n\nID: {call.from_user.id} 🆔\n"
                        f"Foydalanuvchi: {call.from_user.full_name}\n"
                        f"Foydalanuvchi nomi: @{call.from_user.username}\n"
                        f"Telefon raqam: {phone_number}")
        for admin in ADMINS:
            await bot.send_message(chat_id=admin, text=sent_message, reply_markup=checking_number)
        users[user_id] = sent_message
        print(users)
    elif callback == 'verified':
        users_amount.append(user_id)
        this_user = users_amount.count(user_id)
        await call.answer("Tasdiqlandi ✅")
        await bot.send_message(chat_id=user_id,
                               text=f"Ovozingiz tasdiqlandi ✅\nPullaringizni olish uchun 'Admin ☎️' ga telefon "
                                    f"raqamingiz"
                                    f" yoki plastik kartangiz raqamini yozib qoldiring 👇\n\n"
                                    f"Sizning hisobingizda {this_user * 10000} so'm bor",
                               reply_markup=vote_btn)
        await bot.send_message(chat_id=user_id, text="Ovoz berishda davom eting 🗣️👇", reply_markup=voted_btn)
        await call.message.edit_text(text=f"Foydalanuvchi: {phone_number}\n\nFoydalanuvchi hisobida: "
                                          f"{this_user * 10000} so'm bor!")
    elif callback == 'failed':
        this_user = users_amount.count(user_id)
        await call.answer("Bekor qilindi ❌")
        await bot.send_message(chat_id=user_id, text="Ushbu raqam bilan oldinroq ovoz bergansiz ❌\n"
                                                     "Boshqa raqam bilan urinib ko'ring\n\n"
                                                     f"Sizning hisobingizda {this_user * 10000} so'm bor",
                               reply_markup=voted_btn)
        await call.message.edit_text(text=f"Yangi ovoz 🗣️bekor qilindi\n\nID: {call.from_user.id} 🆔\n"
                                          f"Foydalanuvchi: {call.from_user.full_name}\n"
                                          f"Foydalanuvchi nomi: @{call.from_user.username}\n"
                                          f"Telefon raqam: {phone_number}\n\n"
                                          f"Foydalanuvchi hisobida: {this_user * 10000} so'm bor!")
        # await call.message.delete_reply_markup()
    elif callback == 'paid':
        await call.answer("Muvaffaqiyatli yakunlandi ✅")
        await call.message.delete_reply_markup()
    else:
        await call.answer("Error code: 404")
