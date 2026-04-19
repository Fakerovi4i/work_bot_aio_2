import datetime
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import bot
from database import db
from states_group import AdminInsertTasks, AdminAllMessage, AdminOneMessage
from keyboards import (admin_keyboard, admin_choose_ban, admin_choose_unban,
                       admin_break_task_keyboard, key_admin_add_admin, key_admin_dell_admin)

logger = logging.getLogger(__name__)

# ============= КОМАНДА ВХОДА В АДМИНКУ =================
async def admin(message: types.Message, state: FSMContext):
    try:
        if not db.is_admin(message.from_user.id):
            logger.warning(f"Пользователь {message.from_user.id} пытается войти в админку без прав")
            await bot.send_message(
                message.chat.id,
                "Нет прав Администратора⛔"
            )
            return
        logger.info(f"Вход в админку пользователя {message.from_user.id}")
        await bot.send_message(
            message.chat.id,
            " 💻 Ты в админке.\n"
            "Команды: /addadmin | /delladmin\n\n"
            "Выбирай функцию 👇",
            reply_markup=admin_keyboard
        )
    except Exception as e:
        logger.exception(f"Ошибка при входе в админку: {e}")


# ============= ОБРАБОТКА КОМАНД АДМИНКИ =================
async def admin_choose_option(callback: types.CallbackQuery, state: FSMContext):
    try:
        await bot.answer_callback_query(callback.id)
        if not db.is_admin(callback.from_user.id):
            await bot.send_message(
                callback.from_user.id,
                "Нет прав Администратора ⛔"
            )
            logger.info(f"Пользователь {callback.from_user.id} пытается войти в админку без прав")
            return

        action = callback.data.split('_')[1]
        logger.info(f"Админ {callback.from_user.id} выбрал действие {action}")

        if action == "insertTask":
            await bot.send_message(
                callback.from_user.id,
                "✒️ Введи наименование задачи.",
                reply_markup=admin_break_task_keyboard
            )
            await AdminInsertTasks.name.set()

        elif action == "allmess":
            await bot.send_message(callback.from_user.id, "👥 Введи сообщение для отправки всем пользователям.")
            await AdminAllMessage.msg.set()

        elif action == "onemess":
            await bot.send_message(
                callback.from_user.id,
                "📨 Введи сообщение для отправки одному пользователю:",
                reply_markup=admin_break_task_keyboard
            )
            await AdminOneMessage.msg.set()

        elif action == "look":
            improves = db.get_all_improves()
            if not improves:
                await bot.send_message(
                    callback.from_user.id,
                    "Предложений пока нет 😇",
                    reply_markup=admin_keyboard
                )
                return

            senders_from_users = {}
            for call, text in improves:
                if call not in senders_from_users:
                    senders_from_users[call] = []
                senders_from_users[call].append(text)

            message_text = "💡 <b>Предложения и идеи:</b>\n"
            for call, texts in senders_from_users.items():
                name = db.get_user_link_by_callback(call)[0]
                message_text += f"\n👤<code>{name}</code> | <code>callback: {call}</code>\n"
                count = 0
                for text in texts:
                    count += 1
                    message_text += f"{count}. {text}\n"

            # Клавиатура (кнопки назад и Очистить)
            keyboard_back_delete_look = types.InlineKeyboardMarkup(row_width=1)
            b1 = types.InlineKeyboardButton(text='Назад 🔙', callback_data='deletelook_back')
            b2 = types.InlineKeyboardButton(text='Очистить 🧹', callback_data='deletelook_delete')
            keyboard_back_delete_look.add(b1, b2)

            await bot.send_message(
                callback.from_user.id,
                message_text,
                reply_markup=keyboard_back_delete_look,
                parse_mode='HTML'
            )

        elif action == "checkdoc":
            docs = db.get_all_docs()
            if not docs:
                await bot.send_message(
                    callback.from_user.id,
                    "📭 Отчётов пока нет",
                    reply_markup=admin_keyboard,
                    parse_mode='HTML'
                )
                return
            await bot.send_message(
                callback.from_user.id,
                f"📝 <b>{len(docs)} Отчетов</b>\n\n",
                parse_mode='HTML'
            )

            for i, (doc_id, user_id, name, report_text) in enumerate(docs, 1):
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(types.InlineKeyboardButton(
                    text=f"Удалить отчет ❌",
                    callback_data=f"deletedoc_{doc_id}_{user_id}"
                ))

                message_text = f"=== {i} ===\n👤<code>{name}</code> | ID: <code>{user_id}</code>\n{report_text}\n\n"
                await bot.send_message(
                    callback.from_user.id,
                    message_text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )

        elif action == "ban":
            await bot.send_message(
                callback.from_user.id,
                "Выбери кого забанить:",
                reply_markup=admin_choose_ban()
            )

        elif action == "unban":
            if not db.get_users_for_unban_keyboard():
                await bot.send_message(
                    callback.from_user.id,
                    "Нет забаненных пользователей!",
                    reply_markup=admin_keyboard
                )
                return

            await bot.send_message(
                callback.from_user.id,
                "Выбери кого разбанить:",
                reply_markup=admin_choose_unban()
            )
    except Exception as e:
        logger.exception(f"Ошибка админки пользователя {callback.from_user.id}: {e}")


# ============= КОМАНДЫ ДОБАВЛЕНИЯ И УДАЛЕНИЯ АДМИНОВ =================
async def admin_add(message: types.Message, state: FSMContext):
    if not db.is_admin(message.from_user.id):
        await bot.send_message(
            message.chat.id,
            "Нет прав Администратора⛔"
        )
        return

    await bot.send_message(
        message.chat.id,
        "Выбери админа для добавления 💻👇",
        reply_markup=key_admin_add_admin()
    )

async def admin_add_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    call = callback.data.split('_')[1]
    link = db.get_user_link_by_callback(call)[0]
    if db.is_admin(call):
        await bot.send_message(
            callback.from_user.id,
            f"{link} уже Админ 👨‍💻"
        )
        return
    db.add_admin(call, link)
    await bot.send_message(
        callback.from_user.id,
        f"Админ {link} добавлен 👨‍💻"
    )

async def admin_dell(message: types.Message, state: FSMContext):
    if not db.is_admin(message.from_user.id):
        await bot.send_message(
            message.chat.id,
            "Нет прав Администратора⛔"
        )
        return

    if not db.get_admins(message.from_user.id):
        await bot.send_message(
            message.chat.id,
            "Админ только Вы 👨‍💻",
            reply_markup=admin_keyboard
        )
        return

    await bot.send_message(
        message.chat.id,
        "Выбери админа для удаления 👨‍💻👇",
        reply_markup=key_admin_dell_admin(message.from_user.id)
    )

async def admin_dell_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    call = callback.data.split('_')[1]
    link = db.get_user_link_by_callback(call)[0]
    db.delete_admin(call)
    await bot.send_message(
        callback.from_user.id,
        f"Админ {link} удален ❌"
    )


# ====================== УДАЛЕНИЕ ОТЧЕТОВ checkdoc ======================
async def delete_doc(callback: types.CallbackQuery,  state: FSMContext):
    """Удалить отчет по ID-отчета"""
    await bot.answer_callback_query(callback.id)

    doc_id = int(callback.data.split('_')[1])

    db.delete_doc(doc_id)
    await bot.send_message(
        callback.from_user.id,
        f"Отчет №{doc_id} удален ✅",
        reply_markup=admin_keyboard
    )


# ============ УДАЛЕНИЕ СПИСКА ПОЖЕЛАНИЙ =================
async def delete_back_look(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    action = callback.data.split('_')[1]

    if action == 'delete':
        db.delete_all_improves()
        await bot.send_message(
            callback.from_user.id,
            "Предложения и идеи очищены ✅",
            reply_markup=admin_keyboard
        )
    elif action == 'back':
        await bot.send_message(
            callback.from_user.id,
            "Вернулись в админку 👇",
            reply_markup=admin_keyboard
        )


# ============= БАН - РАЗБАН =================
async def admin_want_choose_ban(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    user_to_ban = callback.data.split('_')[1]

    db.ban_user(user_to_ban)
    await bot.send_message(
        callback.from_user.id,
        f"Пользователь {user_to_ban} забанен ⛔",
        reply_markup=admin_keyboard
    )

async def admin_want_choose_unban(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    user_to_unban = callback.data.split('_')[1]

    db.unban_user(user_to_unban)
    await bot.send_message(
        callback.from_user.id,
        f"Пользователь {user_to_unban} разбанен ✅",
        reply_markup=admin_keyboard
    )


# =========== ДОБАВЛЕНИЕ ЗАДАЧИ (4 этапа) ====================
async def admin_nameTask_insert(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['datatime'] = datetime.datetime.today()
        data['name'] = message.text

    await bot.send_message(
        message.chat.id,
        'Принято, введи описание задачи:',
        reply_markup=admin_break_task_keyboard
    )
    await AdminInsertTasks.description.set()

async def admin_desriptionTask_insert(message: types.Message, state: FSMContext):
    '''Добавить описание задачи с кнопками Прервать и Продолжить без фото'''
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text='❌ Прервать', callback_data='admin_break'))
    keyboard.add(types.InlineKeyboardButton(text='📸 Продолжить без фото', callback_data='admin_without_photo'))

    async with state.proxy() as data:
        data['description'] = message.text

    await bot.send_message(
        message.chat.id,
        'Принято, отправь картинку задачи:',
        reply_markup=keyboard
    )
    await AdminInsertTasks.img.set()

async def admin_imgTask_insert(message: types.Message, state: FSMContext):
    """Добавить фото задачи"""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text='❌ Прервать', callback_data='admin_break'))
    keyboard.add(types.InlineKeyboardButton(text='📸 Продолжить без фото', callback_data='admin_without_photo'))

    if not message.photo:
        await bot.send_message(
            message.chat.id,
            "❌ Пожалуйста, отправьте фото задачи.",
            reply_markup=keyboard
        )
        return
    async with state.proxy() as data:
        data['img'] = message.photo[0].file_id

    #Берем не забаненных пользователей
    users = db.get_active_users()
    if not users:
        await bot.send_message(message.chat.id, "😭 Нет активных пользователей")
        await state.finish()
        return

    await bot.send_message(
        message.chat.id,
        f'Выбери callback пользователя и отправь его в чат👇'
    )
    for call, link in users:
        await bot.send_message(
            message.chat.id,
            f"👤{link} | Callback: {call}\n"
        )
    await bot.send_message(
        message.chat.id,
        "Отправь Callback пользователя:",
        reply_markup=admin_break_task_keyboard
    )
    await AdminInsertTasks.callback.set()

async def continue_without_photo(callback: types.CallbackQuery, state: FSMContext):
    """Продолжить добавление задачи без фото"""
    await bot.answer_callback_query(callback.id)
    async with state.proxy() as data:
        data['img'] = 'AgACAgIAAxkBAAIDxWnbysKKzru5JBmYNsY9yYe1cfFKAAI6Imsb4DvhSsIfBJ62V2KvAQADAgADcwADOwQ'

    # Берем не забаненных пользователей
    users = db.get_active_users()
    if not users:
        await bot.send_message(callback.from_user.id, "😭 Нет активных пользователей")
        await state.finish()
        return

    await bot.send_message(
        callback.from_user.id,
        f'Выбери callback пользователя и отправь его в чат👇'
    )
    for call, link in users:
        await bot.send_message(
            callback.from_user.id,
            f"👤{link} | Callback: {call}\n"
        )
    await bot.send_message(
        callback.from_user.id,
        "Отправь Callback пользователя:",
        reply_markup=admin_break_task_keyboard
    )
    await AdminInsertTasks.callback.set()

async def admin_choose_user(message: types.Message, state: FSMContext):
    """Выбрать пользователя для добавления задачи"""
    if not db.get_user_by_callback(message.text.strip()):
        await bot.send_message(
            message.chat.id,
            "❌ Пользователь не найден, введи Callback пользователя:",
            reply_markup=admin_break_task_keyboard
        )
        return
    async with state.proxy() as data:
        data['call'] = message.text.strip()

        db.insert_task(
            datatime=data['datatime'],
            name=data['name'],
            description=data['description'],
            photo=data['img'],
            callback_user=data['call']
        )

    await state.finish()
    await bot.send_message(
        message.chat.id,
        f'Задача добавлена 👍',
        reply_markup=admin_keyboard
    )

async def admin_break_task(callback: types.CallbackQuery, state: FSMContext):
    """Прервать добавление задачи"""
    await bot.answer_callback_query(callback.id)
    await state.finish()
    await bot.send_message(
        callback.from_user.id,
        "❌ Прервано",
        reply_markup=admin_keyboard
    )


# ====================== РАССЫЛКА ВСЕМ ======================
async def admin_send_allmessage(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['msg'] = message.text

        users = db.get_all_users()
        success = 0

        for (call,) in users:
            if int(call) == message.from_user.id:
                continue
            try:
                await bot.send_message(call, data['msg'])
                success += 1
            except:
                db.delete_user(call)

        await state.finish()
        await bot.send_message(
            message.chat.id,
            f"Сообщение отправлено {success} пользователям ✅ ноутбук 🖥\n\n"
            f"Ты в админке 👇",
            reply_markup=admin_keyboard
        )


# ====================== РАССЫЛКА ОДНОМУ ======================
async def admin_send_one_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['msg'] = message.text

    users = db.get_active_users()
    for call, link in users:
        await bot.send_message(
            message.chat.id,
            f"👤{link} | Callback: {call}\n"
        )

    await bot.send_message(
        message.chat.id,
        f'Введи Callback пользователя:',
        reply_markup=admin_break_task_keyboard
    )
    await AdminOneMessage.call.set()

async def admin_send_onecall(message: types.Message, state: FSMContext):
    """Отправить сообщение одному пользователю"""
    if not db.get_user_by_callback(message.text.strip()):
        await bot.send_message(
            message.chat.id,
            "❌ Пользователь не найден, введи Callback пользователя:",
            reply_markup=admin_break_task_keyboard
        )
        return

    async with state.proxy() as data:
        data['call'] = message.text.strip()

        try:
            await bot.send_message(data['call'], data['msg'])
            await state.finish()
            await bot.send_message(
                message.chat.id,
                '✅ Сообщение отправлено\n\nТы в админке.',
                reply_markup=admin_keyboard
            )

        except:
            await state.finish()
            await bot.send_message(
                message.chat.id,
                f'❌ Ошибка отправки\n\nТы в админке.',
                reply_markup=admin_keyboard
            )












