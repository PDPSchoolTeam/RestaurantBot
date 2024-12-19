import asyncio
import logging
import sqlite3
import re
from aiogram import Bot, Dispatcher, F, types, Router
from aiogram.filters import CommandStart, Command
from aiogram.handlers import callback_query
from aiogram.types import Message, CallbackQuery, InputFile
from button import button, sms2, place2
from config import TOKEN, ADMIN
from inline_button import inline_btn, yes_button, delete_button
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime



# Dispatcher va bot
dp = Dispatcher()
bot = Bot(token=TOKEN)
router = Router()

# SQLite bilan bog‘lanish
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Jadvalni yaratish (agar mavjud bo‘lmasa)
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_times (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    user_id INTEGER NOT NULL,
    xona INTEGER NOT NULL,
    time TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    username TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL
)
""")

conn.commit()


# Vaqt formatini tekshirish funksiyasi
def validate_time_format(time_str: str) -> bool:
    return bool(re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", time_str))


# Start komandasi
@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Noma’lum"

    # Foydalanuvchini bazaga qo‘shish
    cursor.execute("""
    INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)
    """, (user_id, username))
    conn.commit()

    if user_id == ADMIN:  # Admin uchun maxsus tugmalar
        await message.answer("Salom Admin, sizga quyidagi menyu taqdim etiladi:", reply_markup=button)
    else:
        await message.answer(
            "😊Assalomu alaykum, botga xush kelibsiz!", reply_markup=inline_btn

        )
        await message.answer("📨FEEDBACK uchun pastdagi tugmani bosing", reply_markup=sms2)


# Callbackni ishlash
@router.callback_query(lambda c: c.data == "alert")
async def inline_button_handler(callback_query: types.CallbackQuery):
    await callback_query.message.answer_photo("https://unsplash.com/photos/empty-building-pathway-lDxxeAJrWpE", caption="☺️Assalomu alaykum botga xush kelibsiz sizni botda ko‘rishdan xursandmiz\n\nSiz bu botda EFendida joylarni band qilishingiz va oldindan taom buyurtma qilishingiz mumkin🍔\n\n/Xonalar 👈 bu buyruq sizga 10 ta xonalar ro‘yxatini taqdim etadi\n\n\nBatafsil ma’lumot olish uchun @Rahimov_MR tg profilga yozing yoki quydagi raqamga telefon qiling +998993666674")
    await bot.answer_callback_query(callback_query.id)

class RoomState(StatesGroup):
    waiting_for_room_number = State()


@dp.callback_query(F.data == "view_bookings")
async def ask_for_room_number(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id == ADMIN:
        await callback_query.message.answer("Qaysi xona raqamini tekshirishni xohlaysiz? Xona raqamini kiriting.")
        await state.set_state(RoomState.waiting_for_room_number)
    else:
        await callback_query.answer("Bu buyruq faqat adminlar uchun mo‘ljallangan!")

# Xona raqamini qabul qilish va bandliklarni ko'rsatish
@dp.message(RoomState.waiting_for_room_number)
async def show_room_bookings(message: Message, state: FSMContext):
    try:
        xona = int(message.text.strip())

        # Ma'lumotlarni bazadan olish
        cursor.execute("SELECT time, username FROM user_times WHERE xona = ?", (xona,))
        results = cursor.fetchall()

        if not results:
            await message.answer(f"🏠 {xona}-xona hozircha band qilingan vaqtlar yo'q.")
        else:
            response = f"🏠 {xona}-xona band qilingan vaqtlar:\n\n"
            for time, username in results:
                response += f"🕒 Vaqt: {time}, 👤 Foydalanuvchi: @{username if username else 'Noma’lum'}\n"

            await message.answer(response)

    except ValueError:
        await message.answer("❌ Xatolik! Iltimos, xona raqamini to‘g‘ri formatda kiriting.")

    # Holatni tugatish
    await state.clear()


@router.callback_query(lambda c: c.data == "zakaz")
async def inline_button_handler(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Xonalarni band qilish boshlandi❗❗❗", reply_markup=place2)


class RoomState(StatesGroup):
    waiting_for_room_number = State()


@dp.message(F.text == "🚫Band qilingan joylarni ko'rish")
async def ask_for_room_number(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN:
        await message.answer("Qaysi xona raqamini tekshirishni xohlaysiz? Xona raqamini kiriting.")
        await state.set_state(RoomState.waiting_for_room_number)
    else:
        await message.answer("Bu buyruq faqat adminlar uchun mo‘ljallangan!")

# Xona raqamini qabul qilish va bandliklarni ko'rsatish
@dp.message(RoomState.waiting_for_room_number)
async def show_room_bookings(message: Message, state: FSMContext):
    try:
        xona = int(message.text.strip())

        # Ma'lumotlarni bazadan olish
        cursor.execute("SELECT time, username FROM user_times WHERE xona = ?", (xona,))
        results = cursor.fetchall()

        if not results:
            await message.answer(f"🏠 {xona}-xona hozircha band qilingan vaqtlar yo'q.")
        else:
            response = f"🏠 {xona}-xona band qilingan vaqtlar:\n\n"
            for time, username in results:
                response += f"🕒 Vaqt: {time}, 👤 Foydalanuvchi: @{username if username else 'Noma’lum'}\n"

            await message.answer(response)

    except ValueError:
        await message.answer("❌ Xatolik! Iltimos, xona raqamini to‘g‘ri formatda kiriting.")

    # Holatni tugatish
    await state.clear()

@dp.message(F.text == "✈️Foydalanuvchilarga malumot yuborish")
async def ask_broadcast_message(message: types.Message):
    await message.answer("Foydalanuvchilarga yuboriladigan xabar matnini kiriting:")

    @dp.message(F.text)
    async def handle_broadcast_message(message: types.Message):
        broadcast_text = message.text.strip()

        # Foydalanuvchilarning user_id'larini olish
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()

        sent_count = 0
        for user in users:
            try:
                await bot.send_message(chat_id=user[0], text=broadcast_text)
                sent_count += 1
            except Exception as e:
                print(f"Xatolik yuz berdi: {e}")

        await message.answer(f"Xabar {sent_count} foydalanuvchiga yuborildi!")



@router.callback_query(lambda c: c.data == "korish")
async def inline_button_handler(callback_query: types.CallbackQuery):
    cursor.execute("SELECT name, description, price FROM foods")
    results = cursor.fetchall()

    if not results:
        await callback_query.message.answer("Hozirda qo'shilgan taomlar yo'q.")
        return

    result_message = "🍽 Taomlar ro'yxati:\n\n"

    for row in results:
        name, description, price = row
        result_message += f"🍴 Taom: {name}\n📝 Ma'lumot: {description}\n💸 Narxi: {price} UZS\n\n"


    await callback_query.message.answer_photo("https://cdn-ijnhp.nitrocdn.com/pywIAllcUPgoWDXtkiXtBgvTOSromKIg/assets/images/optimized/rev-5794eaa/www.jaypeehotels.com/blog/wp-content/uploads/2024/07/Blog-3-scaled.jpg",caption=result_message)



# /Xonalar komandasi
@dp.message(Command("Xonalar"))
async def reply_builder(message: types.Message):
    await message.answer("Xonalardan birini tanlang", reply_markup=place2)


# "Joy-1" xonasi uchun
@dp.message(F.text == "🏠 1")
async def joy_1_handler(message: Message):
    # Foydalanuvchining username'ini tekshirish
    if not message.from_user.username:
        await message.answer("Sizning username'ingiz yo'q. Iltimos, Telegram profil sozlamalariga kirib, username qo'shing.")
        return  # Qayta ishlov berishni to'xtatadi



    # Username mavjud bo'lsa, davom etadi
    await message.answer("1-xona tanlaysizmiz yoki fikiringizni ozgartirasizmi⁉", reply_markup=yes_button)

    @router.callback_query(lambda c: c.data == "room_data")
    async def data_handlers(callback_query: types.CallbackQuery):
        await callback_query.message.answer("📝1-xona haqida ma'lumot\n\nOdamlar soni: 5 ta\n\nXona qulayligi: stol, stul\n\nXonadagi jihozlar: televizor, divan", reply_markup=delete_button)
        await callback_query.answer()

    @router.callback_query(lambda c: c.data == "delete")
    async def delete_handler(callback_query: types.CallbackQuery):
        # Faqat "Xona haqida ma'lumot" xabarini qoldirish uchun boshqa xabarlarni o'chirish
        await callback_query.message.delete()
        await callback_query.answer()


    # "yes" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "yes")
    async def yes_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "1-xona tanlandi. Soat nechiga band qilasiz?\n\nMisol: 15:25"
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # "no" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "no")
    async def no_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "Boshqa xonani tanlashingiz mumkin.",
            reply_markup=place2
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # Vaqtni saqlash funksiyasi
    @dp.message(F.text)
    async def handle_time_input(message: Message):
        time_input = message.text.strip()

        if validate_time_format(time_input):
            # Xonani bandligini tekshirish
            cursor.execute(
                "SELECT time FROM user_times WHERE xona = ?", (1,)
            )
            result = cursor.fetchall()  # Xonaga tegishli barcha vaqtlarni olish

            conflicting_time = None
            for row in result:
                existing_time = row[0]
                # Mavjud vaqtni datetime formatiga o'zgartirish
                existing_datetime = datetime.strptime(existing_time, "%H:%M")
                new_datetime = datetime.strptime(time_input, "%H:%M")

                # 3 soat farqni tekshirish
                time_difference = abs((new_datetime - existing_datetime).total_seconds()) / 3600
                if time_difference < 3:
                    conflicting_time = existing_time
                    break

            if conflicting_time:
                await message.answer(
                    f"Kechirasiz, 1-xona ushbu vaqtda band qilingan: {conflicting_time}. Yangi band qilish vaqti kamida 3 soat farq qilishi kerak."
                )
                return

            try:
                # Ma'lumotlarni bazaga yozish
                cursor.execute(
                    "INSERT INTO user_times (user_id, username, xona, time) VALUES (?, ?, ?, ?)",
                    (message.from_user.id, message.from_user.username, 1, time_input)
                )
                conn.commit()
                await message.answer(f"Vaqt '{time_input}' muvaffaqiyatli saqlandi!")
                await message.answer(
                    f"🧾Sizning chekingiz:\n\n👤Foydalanuvchi ismi: {message.from_user.full_name}\n\nFoydalanuvchi nomi: @{message.from_user.username}\n\n🏠Band qilingan joy: 1-Xona\n\n🕒Vaqt: {time_input}"
                )

            except sqlite3.Error as e:
                await message.answer(f"Xatolik yuz berdi: {e}")
        else:
            await message.answer("Xatolik! Iltimos, vaqtni to‘g‘ri formatda kiriting (masalan, 15:23).")


# Boshqa joylar uchun handlerlar
@dp.message(F.text == "🏠 2")
async def joy_2_handler(message: Message):
    # Foydalanuvchining username'ini tekshirish
    if not message.from_user.username:
        await message.answer(
            "Sizning username'ingiz yo'q. Iltimos, Telegram profil sozlamalariga kirib, username qo'shing.")
        return  # Qayta ishlov berishni to'xtatadi

    # Username mavjud bo'lsa, davom etadi
    await message.answer("2-xona tanlaysizmiz yoki fikiringizni ozgartirasizmi⁉", reply_markup=yes_button)

    @router.callback_query(lambda c: c.data == "room_data")
    async def data_handlers(callback_query: types.CallbackQuery):
        await callback_query.message.answer(
            "📝2-xona haqida malumot\n\nOdamlar soni: 5 ta\n\nXona qulayligi: stol, stul\n\nXonadagi jihozlar: televizor, divan",
            reply_markup=delete_button)
        await callback_query.answer()

    @router.callback_query(lambda c: c.data == "delete")
    async def delete_handler(callback_query: types.CallbackQuery):
        # Faqat "Xona haqida ma'lumot" xabarini qoldirish uchun boshqa xabarlarni o'chirish
        await callback_query.message.delete()
        await callback_query.answer()

    # "yes" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "yes")
    async def yes_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "2-xona tanlandi. Soat nechaga band qilasiz?\n\nMisol: 15:25"
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # "no" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "no")
    async def no_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "Boshqa xonani tanlashingiz mumkin.",
            reply_markup=place2
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # Vaqtni saqlash funksiyasi
    @dp.message(F.text)
    async def handle_time_input(message: Message):
        time_input = message.text.strip()

        if validate_time_format(time_input):
            # Xonani bandligini tekshirish
            cursor.execute(
                "SELECT time FROM user_times WHERE xona = ?", (1,)
            )
            result = cursor.fetchall()  # Xonaga tegishli barcha vaqtlarni olish

            conflicting_time = None
            for row in result:
                existing_time = row[0]
                # Mavjud vaqtni datetime formatiga o'zgartirish
                existing_datetime = datetime.strptime(existing_time, "%H:%M")
                new_datetime = datetime.strptime(time_input, "%H:%M")

                # 3 soat farqni tekshirish
                time_difference = abs((new_datetime - existing_datetime).total_seconds()) / 3600
                if time_difference < 3:
                    conflicting_time = existing_time
                    break

            if conflicting_time:
                await message.answer(
                    f"Kechirasiz, 1-xona ushbu vaqtda band qilingan: {conflicting_time}. Yangi band qilish vaqti kamida 3 soat farq qilishi kerak."
                )
                return

            try:
                # Ma'lumotlarni bazaga yozish
                cursor.execute(
                    "INSERT INTO user_times (user_id, username, xona, time) VALUES (?, ?, ?, ?)",
                    (message.from_user.id, message.from_user.username, 1, time_input)
                )
                conn.commit()
                await message.answer(f"Vaqt '{time_input}' muvaffaqiyatli saqlandi!")
                await message.answer(
                    f"🧾Sizning chekingiz:\n\n👤Foydalanuvchi ismi: {message.from_user.full_name}\n\nFoydalanuvchi nomi: @{message.from_user.username}\n\n🏠Band qilingan joy: 1-Xona\n\n🕒Vaqt: {time_input}"
                )

            except sqlite3.Error as e:
                await message.answer(f"Xatolik yuz berdi: {e}")
        else:
            await message.answer("Xatolik! Iltimos, vaqtni to‘g‘ri formatda kiriting (masalan, 15:23).")


@dp.message(F.text == "🏠 3")
async def joy_3_handler(message: Message):
    # Foydalanuvchining username'ini tekshirish
    if not message.from_user.username:
        await message.answer(
            "Sizning username'ingiz yo'q. Iltimos, Telegram profil sozlamalariga kirib, username qo'shing.")
        return  # Qayta ishlov berishni to'xtatadi

    # Username mavjud bo'lsa, davom etadi
    await message.answer("3-xona tanlaysizmiz yoki fikiringizni ozgartirasizmi⁉", reply_markup=yes_button)

    @router.callback_query(lambda c: c.data == "room_data")
    async def data_handlers(callback_query: types.CallbackQuery):
        await callback_query.message.answer(
            "📝3-xona haqida malumot\n\nOdamlar soni: 5 ta\n\nXona qulayligi: stol, stul\n\nXonadagi jihozlar: televizor, divan",
            reply_markup=delete_button)
        await callback_query.answer()

    @router.callback_query(lambda c: c.data == "delete")
    async def delete_handler(callback_query: types.CallbackQuery):
        # Faqat "Xona haqida ma'lumot" xabarini qoldirish uchun boshqa xabarlarni o'chirish
        await callback_query.message.delete()
        await callback_query.answer()

    # "yes" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "yes")
    async def yes_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "3-xona tanlandi. Soat nechaga band qilasiz?\n\nMisol: 15:25"
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # "no" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "no")
    async def no_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "Boshqa xonani tanlashingiz mumkin.",
            reply_markup=place2
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # Vaqtni saqlash funksiyasi
    @dp.message(F.text)
    async def handle_time_input(message: Message):
        time_input = message.text.strip()

        if validate_time_format(time_input):
            # Xonani bandligini tekshirish
            cursor.execute(
                "SELECT time FROM user_times WHERE xona = ?", (1,)
            )
            result = cursor.fetchall()  # Xonaga tegishli barcha vaqtlarni olish

            conflicting_time = None
            for row in result:
                existing_time = row[0]
                # Mavjud vaqtni datetime formatiga o'zgartirish
                existing_datetime = datetime.strptime(existing_time, "%H:%M")
                new_datetime = datetime.strptime(time_input, "%H:%M")

                # 3 soat farqni tekshirish
                time_difference = abs((new_datetime - existing_datetime).total_seconds()) / 3600
                if time_difference < 3:
                    conflicting_time = existing_time
                    break

            if conflicting_time:
                await message.answer(
                    f"Kechirasiz, 1-xona ushbu vaqtda band qilingan: {conflicting_time}. Yangi band qilish vaqti kamida 3 soat farq qilishi kerak."
                )
                return

            try:
                # Ma'lumotlarni bazaga yozish
                cursor.execute(
                    "INSERT INTO user_times (user_id, username, xona, time) VALUES (?, ?, ?, ?)",
                    (message.from_user.id, message.from_user.username, 1, time_input)
                )
                conn.commit()
                await message.answer(f"Vaqt '{time_input}' muvaffaqiyatli saqlandi!")
                await message.answer(
                    f"🧾Sizning chekingiz:\n\n👤Foydalanuvchi ismi: {message.from_user.full_name}\n\nFoydalanuvchi nomi: @{message.from_user.username}\n\n🏠Band qilingan joy: 1-Xona\n\n🕒Vaqt: {time_input}"
                )

            except sqlite3.Error as e:
                await message.answer(f"Xatolik yuz berdi: {e}")
        else:
            await message.answer("Xatolik! Iltimos, vaqtni to‘g‘ri formatda kiriting (masalan, 15:23).")




@dp.message(F.text == "🏠 4")
async def joy_3_handler(message: Message):
    # Foydalanuvchining username'ini tekshirish
    if not message.from_user.username:
        await message.answer(
            "Sizning username'ingiz yo'q. Iltimos, Telegram profil sozlamalariga kirib, username qo'shing.")
        return  # Qayta ishlov berishni to'xtatadi

    # Username mavjud bo'lsa, davom etadi
    await message.answer("4-xona tanlaysizmiz yoki fikiringizni ozgartirasizmi⁉", reply_markup=yes_button)

    @router.callback_query(lambda c: c.data == "room_data")
    async def data_handlers(callback_query: types.CallbackQuery):
        await callback_query.message.answer(
            "📝4-xona haqida malumot\n\nOdamlar soni: 5 ta\n\nXona qulayligi: stol, stul\n\nXonadagi jihozlar: televizor, divan",
            reply_markup=delete_button)
        await callback_query.answer()

    @router.callback_query(lambda c: c.data == "delete")
    async def delete_handler(callback_query: types.CallbackQuery):
        # Faqat "Xona haqida ma'lumot" xabarini qoldirish uchun boshqa xabarlarni o'chirish
        await callback_query.message.delete()
        await callback_query.answer()

    # "yes" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "yes")
    async def yes_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "4-xona tanlandi. Soat nechaga band qilasiz?\n\nMisol: 15:25"
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # "no" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "no")
    async def no_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "Boshqa xonani tanlashingiz mumkin.",
            reply_markup=place2
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # Vaqtni saqlash funksiyasi
    @dp.message(F.text)
    async def handle_time_input(message: Message):
        time_input = message.text.strip()

        if validate_time_format(time_input):
            # Xonani bandligini tekshirish
            cursor.execute(
                "SELECT time FROM user_times WHERE xona = ?", (1,)
            )
            result = cursor.fetchall()  # Xonaga tegishli barcha vaqtlarni olish

            conflicting_time = None
            for row in result:
                existing_time = row[0]
                # Mavjud vaqtni datetime formatiga o'zgartirish
                existing_datetime = datetime.strptime(existing_time, "%H:%M")
                new_datetime = datetime.strptime(time_input, "%H:%M")

                # 3 soat farqni tekshirish
                time_difference = abs((new_datetime - existing_datetime).total_seconds()) / 3600
                if time_difference < 3:
                    conflicting_time = existing_time
                    break

            if conflicting_time:
                await message.answer(
                    f"Kechirasiz, 1-xona ushbu vaqtda band qilingan: {conflicting_time}. Yangi band qilish vaqti kamida 3 soat farq qilishi kerak."
                )
                return

            try:
                # Ma'lumotlarni bazaga yozish
                cursor.execute(
                    "INSERT INTO user_times (user_id, username, xona, time) VALUES (?, ?, ?, ?)",
                    (message.from_user.id, message.from_user.username, 1, time_input)
                )
                conn.commit()
                await message.answer(f"Vaqt '{time_input}' muvaffaqiyatli saqlandi!")
                await message.answer(
                    f"🧾Sizning chekingiz:\n\n👤Foydalanuvchi ismi: {message.from_user.full_name}\n\nFoydalanuvchi nomi: @{message.from_user.username}\n\n🏠Band qilingan joy: 1-Xona\n\n🕒Vaqt: {time_input}"
                )

            except sqlite3.Error as e:
                await message.answer(f"Xatolik yuz berdi: {e}")
        else:
            await message.answer("Xatolik! Iltimos, vaqtni to‘g‘ri formatda kiriting (masalan, 15:23).")




@dp.message(F.text == "🏠 5")
async def joy_3_handler(message: Message):
    # Foydalanuvchining username'ini tekshirish
    if not message.from_user.username:
        await message.answer(
            "Sizning username'ingiz yo'q. Iltimos, Telegram profil sozlamalariga kirib, username qo'shing.")
        return  # Qayta ishlov berishni to'xtatadi

    # Username mavjud bo'lsa, davom etadi
    await message.answer("5-xona tanlaysizmiz yoki fikiringizni ozgartirasizmi⁉", reply_markup=yes_button)

    @router.callback_query(lambda c: c.data == "room_data")
    async def data_handlers(callback_query: types.CallbackQuery):
        await callback_query.message.answer(
            "📝5-xona haqida malumot\n\nOdamlar soni: 5 ta\n\nXona qulayligi: stol, stul\n\nXonadagi jihozlar: televizor, divan",
            reply_markup=delete_button)
        await callback_query.answer()

    @router.callback_query(lambda c: c.data == "delete")
    async def delete_handler(callback_query: types.CallbackQuery):
        # Faqat "Xona haqida ma'lumot" xabarini qoldirish uchun boshqa xabarlarni o'chirish
        await callback_query.message.delete()
        await callback_query.answer()

    # "yes" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "yes")
    async def yes_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "5-xona tanlandi. Soat nechaga band qilasiz?\n\nMisol: 15:25"
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # "no" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "no")
    async def no_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "Boshqa xonani tanlashingiz mumkin.",
            reply_markup=place2
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # Vaqtni saqlash funksiyasi
    @dp.message(F.text)
    async def handle_time_input(message: Message):
        time_input = message.text.strip()

        if validate_time_format(time_input):
            # Xonani bandligini tekshirish
            cursor.execute(
                "SELECT time FROM user_times WHERE xona = ?", (1,)
            )
            result = cursor.fetchall()  # Xonaga tegishli barcha vaqtlarni olish

            conflicting_time = None
            for row in result:
                existing_time = row[0]
                # Mavjud vaqtni datetime formatiga o'zgartirish
                existing_datetime = datetime.strptime(existing_time, "%H:%M")
                new_datetime = datetime.strptime(time_input, "%H:%M")

                # 3 soat farqni tekshirish
                time_difference = abs((new_datetime - existing_datetime).total_seconds()) / 3600
                if time_difference < 3:
                    conflicting_time = existing_time
                    break

            if conflicting_time:
                await message.answer(
                    f"Kechirasiz, 1-xona ushbu vaqtda band qilingan: {conflicting_time}. Yangi band qilish vaqti kamida 3 soat farq qilishi kerak."
                )
                return

            try:
                # Ma'lumotlarni bazaga yozish
                cursor.execute(
                    "INSERT INTO user_times (user_id, username, xona, time) VALUES (?, ?, ?, ?)",
                    (message.from_user.id, message.from_user.username, 1, time_input)
                )
                conn.commit()
                await message.answer(f"Vaqt '{time_input}' muvaffaqiyatli saqlandi!")
                await message.answer(
                    f"🧾Sizning chekingiz:\n\n👤Foydalanuvchi ismi: {message.from_user.full_name}\n\nFoydalanuvchi nomi: @{message.from_user.username}\n\n🏠Band qilingan joy: 1-Xona\n\n🕒Vaqt: {time_input}"
                )

            except sqlite3.Error as e:
                await message.answer(f"Xatolik yuz berdi: {e}")
        else:
            await message.answer("Xatolik! Iltimos, vaqtni to‘g‘ri formatda kiriting (masalan, 15:23).")



@dp.message(F.text == "🏠 6")
async def joy_3_handler(message: Message):
    # Foydalanuvchining username'ini tekshirish
    if not message.from_user.username:
        await message.answer(
            "Sizning username'ingiz yo'q. Iltimos, Telegram profil sozlamalariga kirib, username qo'shing.")
        return  # Qayta ishlov berishni to'xtatadi

    # Username mavjud bo'lsa, davom etadi
    await message.answer("6-xona tanlaysizmiz yoki fikiringizni ozgartirasizmi⁉", reply_markup=yes_button)

    @router.callback_query(lambda c: c.data == "room_data")
    async def data_handlers(callback_query: types.CallbackQuery):
        await callback_query.message.answer(
            "📝6-xona haqida malumot\n\nOdamlar soni: 5 ta\n\nXona qulayligi: stol, stul\n\nXonadagi jihozlar: televizor, divan",
            reply_markup=delete_button)
        await callback_query.answer()

    @router.callback_query(lambda c: c.data == "delete")
    async def delete_handler(callback_query: types.CallbackQuery):
        # Faqat "Xona haqida ma'lumot" xabarini qoldirish uchun boshqa xabarlarni o'chirish
        await callback_query.message.delete()
        await callback_query.answer()

    # "yes" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "yes")
    async def yes_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "6-xona tanlandi. Soat nechaga band qilasiz?\n\nMisol: 15:25"
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # "no" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "no")
    async def no_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "Boshqa xonani tanlashingiz mumkin.",
            reply_markup=place2
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # Vaqtni saqlash funksiyasi
    @dp.message(F.text)
    async def handle_time_input(message: Message):
        time_input = message.text.strip()

        if validate_time_format(time_input):
            # Xonani bandligini tekshirish
            cursor.execute(
                "SELECT time FROM user_times WHERE xona = ?", (1,)
            )
            result = cursor.fetchall()  # Xonaga tegishli barcha vaqtlarni olish

            conflicting_time = None
            for row in result:
                existing_time = row[0]
                # Mavjud vaqtni datetime formatiga o'zgartirish
                existing_datetime = datetime.strptime(existing_time, "%H:%M")
                new_datetime = datetime.strptime(time_input, "%H:%M")

                # 3 soat farqni tekshirish
                time_difference = abs((new_datetime - existing_datetime).total_seconds()) / 3600
                if time_difference < 3:
                    conflicting_time = existing_time
                    break

            if conflicting_time:
                await message.answer(
                    f"Kechirasiz, 1-xona ushbu vaqtda band qilingan: {conflicting_time}. Yangi band qilish vaqti kamida 3 soat farq qilishi kerak."
                )
                return

            try:
                # Ma'lumotlarni bazaga yozish
                cursor.execute(
                    "INSERT INTO user_times (user_id, username, xona, time) VALUES (?, ?, ?, ?)",
                    (message.from_user.id, message.from_user.username, 1, time_input)
                )
                conn.commit()
                await message.answer(f"Vaqt '{time_input}' muvaffaqiyatli saqlandi!")
                await message.answer(
                    f"🧾Sizning chekingiz:\n\n👤Foydalanuvchi ismi: {message.from_user.full_name}\n\nFoydalanuvchi nomi: @{message.from_user.username}\n\n🏠Band qilingan joy: 1-Xona\n\n🕒Vaqt: {time_input}"
                )

            except sqlite3.Error as e:
                await message.answer(f"Xatolik yuz berdi: {e}")
        else:
            await message.answer("Xatolik! Iltimos, vaqtni to‘g‘ri formatda kiriting (masalan, 15:23).")



@dp.message(F.text == "🏠 7")
async def joy_3_handler(message: Message):
    # Foydalanuvchining username'ini tekshirish
    if not message.from_user.username:
        await message.answer(
            "Sizning username'ingiz yo'q. Iltimos, Telegram profil sozlamalariga kirib, username qo'shing.")
        return  # Qayta ishlov berishni to'xtatadi

    # Username mavjud bo'lsa, davom etadi
    await message.answer("7-xona tanlaysizmiz yoki fikiringizni ozgartirasizmi⁉", reply_markup=yes_button)

    @router.callback_query(lambda c: c.data == "room_data")
    async def data_handlers(callback_query: types.CallbackQuery):
        await callback_query.message.answer(
            "📝7-xona haqida malumot\n\nOdamlar soni: 5 ta\n\nXona qulayligi: stol, stul\n\nXonadagi jihozlar: televizor, divan",
            reply_markup=delete_button)
        await callback_query.answer()

    @router.callback_query(lambda c: c.data == "delete")
    async def delete_handler(callback_query: types.CallbackQuery):
        # Faqat "Xona haqida ma'lumot" xabarini qoldirish uchun boshqa xabarlarni o'chirish
        await callback_query.message.delete()
        await callback_query.answer()

    # "yes" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "yes")
    async def yes_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "7-xona tanlandi. Soat nechaga band qilasiz?\n\nMisol: 15:25"
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # "no" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "no")
    async def no_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "Boshqa xonani tanlashingiz mumkin.",
            reply_markup=place2
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # Vaqtni saqlash funksiyasi
    @dp.message(F.text)
    async def handle_time_input(message: Message):
        time_input = message.text.strip()

        if validate_time_format(time_input):
            # Xonani bandligini tekshirish
            cursor.execute(
                "SELECT time FROM user_times WHERE xona = ?", (1,)
            )
            result = cursor.fetchall()  # Xonaga tegishli barcha vaqtlarni olish

            conflicting_time = None
            for row in result:
                existing_time = row[0]
                # Mavjud vaqtni datetime formatiga o'zgartirish
                existing_datetime = datetime.strptime(existing_time, "%H:%M")
                new_datetime = datetime.strptime(time_input, "%H:%M")

                # 3 soat farqni tekshirish
                time_difference = abs((new_datetime - existing_datetime).total_seconds()) / 3600
                if time_difference < 3:
                    conflicting_time = existing_time
                    break

            if conflicting_time:
                await message.answer(
                    f"Kechirasiz, 1-xona ushbu vaqtda band qilingan: {conflicting_time}. Yangi band qilish vaqti kamida 3 soat farq qilishi kerak."
                )
                return

            try:
                # Ma'lumotlarni bazaga yozish
                cursor.execute(
                    "INSERT INTO user_times (user_id, username, xona, time) VALUES (?, ?, ?, ?)",
                    (message.from_user.id, message.from_user.username, 1, time_input)
                )
                conn.commit()
                await message.answer(f"Vaqt '{time_input}' muvaffaqiyatli saqlandi!")
                await message.answer(
                    f"🧾Sizning chekingiz:\n\n👤Foydalanuvchi ismi: {message.from_user.full_name}\n\nFoydalanuvchi nomi: @{message.from_user.username}\n\n🏠Band qilingan joy: 1-Xona\n\n🕒Vaqt: {time_input}"
                )

            except sqlite3.Error as e:
                await message.answer(f"Xatolik yuz berdi: {e}")
        else:
            await message.answer("Xatolik! Iltimos, vaqtni to‘g‘ri formatda kiriting (masalan, 15:23).")



@dp.message(F.text == "🏠 8")
async def joy_3_handler(message: Message):
    # Foydalanuvchining username'ini tekshirish
    if not message.from_user.username:
        await message.answer(
            "Sizning username'ingiz yo'q. Iltimos, Telegram profil sozlamalariga kirib, username qo'shing.")
        return  # Qayta ishlov berishni to'xtatadi

    # Username mavjud bo'lsa, davom etadi
    await message.answer("8-xona tanlaysizmiz yoki fikiringizni ozgartirasizmi⁉", reply_markup=yes_button)

    @router.callback_query(lambda c: c.data == "room_data")
    async def data_handlers(callback_query: types.CallbackQuery):
        await callback_query.message.answer(
            "📝8-xona haqida malumot\n\nOdamlar soni: 5 ta\n\nXona qulayligi: stol, stul\n\nXonadagi jihozlar: televizor, divan",
            reply_markup=delete_button)
        await callback_query.answer()

    @router.callback_query(lambda c: c.data == "delete")
    async def delete_handler(callback_query: types.CallbackQuery):
        # Faqat "Xona haqida ma'lumot" xabarini qoldirish uchun boshqa xabarlarni o'chirish
        await callback_query.message.delete()
        await callback_query.answer()

    # "yes" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "yes")
    async def yes_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "8-xona tanlandi. Soat nechaga band qilasiz?\n\nMisol: 15:25"
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # "no" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "no")
    async def no_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "Boshqa xonani tanlashingiz mumkin.",
            reply_markup=place2
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # Vaqtni saqlash funksiyasi
    @dp.message(F.text)
    async def handle_time_input(message: Message):
        time_input = message.text.strip()

        if validate_time_format(time_input):
            # Xonani bandligini tekshirish
            cursor.execute(
                "SELECT time FROM user_times WHERE xona = ?", (1,)
            )
            result = cursor.fetchall()  # Xonaga tegishli barcha vaqtlarni olish

            conflicting_time = None
            for row in result:
                existing_time = row[0]
                # Mavjud vaqtni datetime formatiga o'zgartirish
                existing_datetime = datetime.strptime(existing_time, "%H:%M")
                new_datetime = datetime.strptime(time_input, "%H:%M")

                # 3 soat farqni tekshirish
                time_difference = abs((new_datetime - existing_datetime).total_seconds()) / 3600
                if time_difference < 3:
                    conflicting_time = existing_time
                    break

            if conflicting_time:
                await message.answer(
                    f"Kechirasiz, 1-xona ushbu vaqtda band qilingan: {conflicting_time}. Yangi band qilish vaqti kamida 3 soat farq qilishi kerak."
                )
                return

            try:
                # Ma'lumotlarni bazaga yozish
                cursor.execute(
                    "INSERT INTO user_times (user_id, username, xona, time) VALUES (?, ?, ?, ?)",
                    (message.from_user.id, message.from_user.username, 1, time_input)
                )
                conn.commit()
                await message.answer(f"Vaqt '{time_input}' muvaffaqiyatli saqlandi!")
                await message.answer(
                    f"🧾Sizning chekingiz:\n\n👤Foydalanuvchi ismi: {message.from_user.full_name}\n\nFoydalanuvchi nomi: @{message.from_user.username}\n\n🏠Band qilingan joy: 1-Xona\n\n🕒Vaqt: {time_input}"
                )

            except sqlite3.Error as e:
                await message.answer(f"Xatolik yuz berdi: {e}")
        else:
            await message.answer("Xatolik! Iltimos, vaqtni to‘g‘ri formatda kiriting (masalan, 15:23).")



@dp.message(F.text == "🏠 9")
async def joy_3_handler(message: Message):
    # Foydalanuvchining username'ini tekshirish
    if not message.from_user.username:
        await message.answer(
            "Sizning username'ingiz yo'q. Iltimos, Telegram profil sozlamalariga kirib, username qo'shing.")
        return  # Qayta ishlov berishni to'xtatadi

    # Username mavjud bo'lsa, davom etadi
    await message.answer("9-xona tanlaysizmiz yoki fikiringizni ozgartirasizmi⁉", reply_markup=yes_button)

    @router.callback_query(lambda c: c.data == "room_data")
    async def data_handlers(callback_query: types.CallbackQuery):
        await callback_query.message.answer(
            "📝9-xona haqida malumot\n\nOdamlar soni: 5 ta\n\nXona qulayligi: stol, stul\n\nXonadagi jihozlar: televizor, divan",
            reply_markup=delete_button)
        await callback_query.answer()

    @router.callback_query(lambda c: c.data == "delete")
    async def delete_handler(callback_query: types.CallbackQuery):
        # Faqat "Xona haqida ma'lumot" xabarini qoldirish uchun boshqa xabarlarni o'chirish
        await callback_query.message.delete()
        await callback_query.answer()

    # "yes" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "yes")
    async def yes_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "9-xona tanlandi. Soat nechaga band qilasiz?\n\nMisol: 15:25"
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # "no" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "no")
    async def no_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "Boshqa xonani tanlashingiz mumkin.",
            reply_markup=place2
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # Vaqtni saqlash funksiyasi
    @dp.message(F.text)
    async def handle_time_input(message: Message):
        time_input = message.text.strip()

        if validate_time_format(time_input):
            # Xonani bandligini tekshirish
            cursor.execute(
                "SELECT time FROM user_times WHERE xona = ?", (1,)
            )
            result = cursor.fetchall()  # Xonaga tegishli barcha vaqtlarni olish

            conflicting_time = None
            for row in result:
                existing_time = row[0]
                # Mavjud vaqtni datetime formatiga o'zgartirish
                existing_datetime = datetime.strptime(existing_time, "%H:%M")
                new_datetime = datetime.strptime(time_input, "%H:%M")

                # 3 soat farqni tekshirish
                time_difference = abs((new_datetime - existing_datetime).total_seconds()) / 3600
                if time_difference < 3:
                    conflicting_time = existing_time
                    break

            if conflicting_time:
                await message.answer(
                    f"Kechirasiz, 1-xona ushbu vaqtda band qilingan: {conflicting_time}. Yangi band qilish vaqti kamida 3 soat farq qilishi kerak."
                )
                return

            try:
                # Ma'lumotlarni bazaga yozish
                cursor.execute(
                    "INSERT INTO user_times (user_id, username, xona, time) VALUES (?, ?, ?, ?)",
                    (message.from_user.id, message.from_user.username, 1, time_input)
                )
                conn.commit()
                await message.answer(f"Vaqt '{time_input}' muvaffaqiyatli saqlandi!")
                await message.answer(
                    f"🧾Sizning chekingiz:\n\n👤Foydalanuvchi ismi: {message.from_user.full_name}\n\nFoydalanuvchi nomi: @{message.from_user.username}\n\n🏠Band qilingan joy: 1-Xona\n\n🕒Vaqt: {time_input}"
                )

            except sqlite3.Error as e:
                await message.answer(f"Xatolik yuz berdi: {e}")
        else:
            await message.answer("Xatolik! Iltimos, vaqtni to‘g‘ri formatda kiriting (masalan, 15:23).")



@dp.message(F.text == "🏠 10")
async def joy_3_handler(message: Message):
    # Foydalanuvchining username'ini tekshirish
    if not message.from_user.username:
        await message.answer(
            "Sizning username'ingiz yo'q. Iltimos, Telegram profil sozlamalariga kirib, username qo'shing.")
        return  # Qayta ishlov berishni to'xtatadi

    # Username mavjud bo'lsa, davom etadi
    await message.answer("10-xona tanlaysizmiz yoki fikiringizni ozgartirasizmi⁉", reply_markup=yes_button)

    @router.callback_query(lambda c: c.data == "room_data")
    async def data_handlers(callback_query: types.CallbackQuery):
        await callback_query.message.answer(
            "📝10-xona haqida malumot\n\nOdamlar soni: 5 ta\n\nXona qulayligi: stol, stul\n\nXonadagi jihozlar: televizor, divan",
            reply_markup=delete_button)
        await callback_query.answer()

    @router.callback_query(lambda c: c.data == "delete")
    async def delete_handler(callback_query: types.CallbackQuery):
        # Faqat "Xona haqida ma'lumot" xabarini qoldirish uchun boshqa xabarlarni o'chirish
        await callback_query.message.delete()
        await callback_query.answer()

    # "yes" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "yes")
    async def yes_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "10-xona tanlandi. Soat nechaga band qilasiz?\n\nMisol: 15:25"
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # "no" tugmasi uchun handler
    @router.callback_query(lambda c: c.data == "no")
    async def no_handler(callback_query: types.CallbackQuery):
        # Xabarni yashirish
        await callback_query.message.delete()

        # Yangi xabar yuborish
        await callback_query.message.answer(
            "Boshqa xonani tanlashingiz mumkin.",
            reply_markup=place2
        )
        await callback_query.answer()  # Callback "loading"ni yopish

    # Vaqtni saqlash funksiyasi
    @dp.message(F.text)
    async def handle_time_input(message: Message):
        time_input = message.text.strip()

        if validate_time_format(time_input):
            # Xonani bandligini tekshirish
            cursor.execute(
                "SELECT time FROM user_times WHERE xona = ?", (1,)
            )
            result = cursor.fetchall()  # Xonaga tegishli barcha vaqtlarni olish

            conflicting_time = None
            for row in result:
                existing_time = row[0]
                # Mavjud vaqtni datetime formatiga o'zgartirish
                existing_datetime = datetime.strptime(existing_time, "%H:%M")
                new_datetime = datetime.strptime(time_input, "%H:%M")

                # 3 soat farqni tekshirish
                time_difference = abs((new_datetime - existing_datetime).total_seconds()) / 3600
                if time_difference < 3:
                    conflicting_time = existing_time
                    break

            if conflicting_time:
                await message.answer(
                    f"Kechirasiz, 1-xona ushbu vaqtda band qilingan: {conflicting_time}. Yangi band qilish vaqti kamida 3 soat farq qilishi kerak."
                )
                return

            try:
                # Ma'lumotlarni bazaga yozish
                cursor.execute(
                    "INSERT INTO user_times (user_id, username, xona, time) VALUES (?, ?, ?, ?)",
                    (message.from_user.id, message.from_user.username, 1, time_input)
                )
                conn.commit()
                await message.answer(f"Vaqt '{time_input}' muvaffaqiyatli saqlandi!")
                await message.answer(
                    f"🧾Sizning chekingiz:\n\n👤Foydalanuvchi ismi: {message.from_user.full_name}\n\nFoydalanuvchi nomi: @{message.from_user.username}\n\n🏠Band qilingan joy: 1-Xona\n\n🕒Vaqt: {time_input}"
                )

            except sqlite3.Error as e:
                await message.answer(f"Xatolik yuz berdi: {e}")
        else:
            await message.answer("Xatolik! Iltimos, vaqtni to‘g‘ri formatda kiriting (masalan, 15:23).")


@dp.message(F.text == "🔙Orqaga qaytish")
async def qaytish_handler(message: Message):
    await message.answer("🔙Orqaga qaytildi", reply_markup=sms2)


@dp.message(F.text.startswith("✂️Xonani o'chirish:"))
async def delete_room_handler(message: Message):
    if message.from_user.id != ADMIN:
        await message.answer("Sizda bu buyruqni bajarish huquqi yo'q!")
        return

    await message.answer("Qaysi xonaning qaysi vaqtini o'chirasiz? Misol: 3, 14:20")

    @dp.message()
    async def process_deletion_input(input_message: Message):
        if input_message.from_user.id != ADMIN:
            await input_message.answer("Sizda bu buyruqni bajarish huquqi yo'q!")
            return

        try:
            if "," not in input_message.text:
                await input_message.answer("Xatolik! Ma'lumot formati noto'g'ri. Misol: 3, 14:20")
                return

            xona_str, vaqt = input_message.text.split(",")
            xona = int(xona_str.strip())
            vaqt = vaqt.strip()

            if not validate_time_format(vaqt):
                await input_message.answer("Xatolik! Vaqt formati noto'g'ri. Misol: 3, 14:20")
                return
        except (ValueError, IndexError):
            await input_message.answer("Xatolik! Ma'lumot formati noto'g'ri. Misol: 3, 14:20")
            return

        # Xonani bandlikdan o‘chirish
        cursor.execute("DELETE FROM user_times WHERE xona = ? AND time = ?", (xona, vaqt))
        conn.commit()

        if cursor.rowcount > 0:
            await input_message.answer(f"🏠 {xona}-xona {vaqt} vaqtidagi bandlik muvaffaqiyatli o'chirildi.")
        else:
            await input_message.answer(f"Xatolik! 🏠 {xona}-xona {vaqt} vaqtidagi bandlik topilmadi.")




class AddFoodState(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()




@dp.message(F.text == "🆕Manuga taom qoshish")
async def add_food_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN:
        await message.answer("Bu buyruq faqat adminlar uchun!")
        return

    await message.answer("Ovqat nomini kiriting:")
    await state.set_state(AddFoodState.waiting_for_name)


@dp.message(AddFoodState.waiting_for_name)
async def add_food_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Ovqat tavsifini kiriting:")
    await state.set_state(AddFoodState.waiting_for_description)


@dp.message(AddFoodState.waiting_for_description)
async def add_food_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await message.answer("Ovqat narxini kiriting (faqat son):")
    await state.set_state(AddFoodState.waiting_for_price)


@dp.message(AddFoodState.waiting_for_price)
async def add_food_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.strip())
        data = await state.get_data()
        food_name = data['name']
        food_description = data['description']

        # Ovqatni ma'lumotlar bazasiga qo'shish
        cursor.execute("""
            INSERT INTO foods (name, description, price)
            VALUES (?, ?, ?)
        """, (food_name, food_description, price))
        conn.commit()

        await message.answer(f"✅ Ovqat qo'shildi:\n\n🍴 Nomi: {food_name}\n📄 Tavsif: {food_description}\n💰 Narxi: {price} UZS")
        await state.clear()

    except ValueError:
        await message.answer("❌ Xato! Narxni son shaklida kiriting.")








# Botni ishga tushirish
dp.include_router(router)

# Asosiy funksiyani ishga tushirish
async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())