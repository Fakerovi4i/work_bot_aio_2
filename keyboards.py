from aiogram import types
from database import db


def keyboard_start():
    start_keyboard = types.InlineKeyboardMarkup(row_width=1)
    start_b1 = types.InlineKeyboardButton(text='ℹ️ Инструкция', callback_data='start_info')

    start_b2 = types.InlineKeyboardButton(text='🦾 Помощь AI Ассистента', callback_data='start_AI')
    start_b3 = types.InlineKeyboardButton(text='📋 Задачи', callback_data='start_tasks')
    start_b4 = types.InlineKeyboardButton(text='⏰ Отметиться', callback_data='start_inwork')
    start_b5 = types.InlineKeyboardButton(text='💡 Внести пожелание', callback_data='start_sendsome')
    start_b6 = types.InlineKeyboardButton(text='📉 Отправить отчет', callback_data='start_document')

    start_keyboard.add(start_b1, start_b3, start_b4, start_b6, start_b2, start_b5)
    return start_keyboard

def keyboard_inwork():
    inwork_keyboard = types.InlineKeyboardMarkup(row_width=1)
    inwork_b1 = types.InlineKeyboardButton(text='👩‍🦯‍➡️ Пришел', callback_data='inwork_come')
    inwork_b2 = types.InlineKeyboardButton(text='🧑‍🦽 Ушел', callback_data='inwork_out')
    inwork_keyboard.add(inwork_b1, inwork_b2)
    return inwork_keyboard

def keyboard_admin():
    admin_start = types.InlineKeyboardMarkup(row_width=1)
    admin_b1 = types.InlineKeyboardButton(text='📊📌 Добавить задачу', callback_data='admin_insertTask')
    admin_b2 = types.InlineKeyboardButton(text='👥 Отправить сообщение всем', callback_data='admin_allmess')
    admin_b3 = types.InlineKeyboardButton(text='👤 Отправить сообщение одному', callback_data='admin_onemess')
    admin_b4 = types.InlineKeyboardButton(text='💡 Посмотреть предложения и идеи', callback_data='admin_look')
    admin_b5 = types.InlineKeyboardButton(text='📉 Посмотреть отчеты', callback_data='admin_checkdoc')
    admin_b6 = types.InlineKeyboardButton(text='⛔ Забанить Пользователя', callback_data='admin_ban')
    admin_b7 = types.InlineKeyboardButton(text='✅ Разбанить Пользователя', callback_data='admin_unban')
    admin_start.add(admin_b1, admin_b2, admin_b3, admin_b4, admin_b5, admin_b6, admin_b7)
    return admin_start

def keyboard_admin_break():
    admin_break = types.InlineKeyboardMarkup(row_width=1)
    b1 = types.InlineKeyboardButton(text='❌ Прервать', callback_data='admin_break')
    admin_break.add(b1)
    return admin_break

def admin_choose_ban():
    key_for_ban = types.InlineKeyboardMarkup(row_width=1)
    for call, link in db.get_active_users():
        key_for_ban.add(types.InlineKeyboardButton(text=f"{link}", callback_data=f"ban_{call}"))
    return key_for_ban

def admin_choose_unban():
    key_for_unban = types.InlineKeyboardMarkup(row_width=1)
    for call, link in db.get_users_for_unban_keyboard():
        key_for_unban.add(types.InlineKeyboardButton(text=f"{link}", callback_data=f"unban_{call}"))
    return key_for_unban

def keyboard_ai():
    ai_keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    ai_b1 = types.InlineKeyboardButton(text='Выйти из AI режима', callback_data='ai_exit')
    ai_keyboard.add(ai_b1)
    return ai_keyboard

def key_admin_add_admin():
    key_for_add_admin = types.InlineKeyboardMarkup(row_width=1)

    for call, link in db.get_active_users():
        key_for_add_admin.add(types.InlineKeyboardButton(text=f"{link}", callback_data=f"addadmin_{call}"))
    return key_for_add_admin

def key_admin_dell_admin(call_asking):
    key_for_dell_admin = types.InlineKeyboardMarkup(row_width=1)
    for call, link in db.get_admins(call_asking):
        key_for_dell_admin.add(types.InlineKeyboardButton(text=f"{link}", callback_data=f"delladmin_{call}"))
    return key_for_dell_admin

keyboard_start = keyboard_start()
inwork_keyboard = keyboard_inwork()
admin_keyboard = keyboard_admin()
ai_keyboard = keyboard_ai()
admin_break_task_keyboard = keyboard_admin_break()
