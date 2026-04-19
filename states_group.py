from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminInsertTasks(StatesGroup):
    name = State()
    description = State()
    img = State()
    callback = State()


class AdminAllMessage(StatesGroup):
    msg = State()

class AdminOneMessage(StatesGroup):
    msg = State()
    call = State()

class UserSendSome(StatesGroup):
    msg = State()

class UserSendDoc(StatesGroup):
    doc = State()


class UserChatWithAI(StatesGroup):
    chatting = State()
