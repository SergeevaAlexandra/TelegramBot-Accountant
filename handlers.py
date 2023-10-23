from aiogram import types, Router
from aiogram.filters import Command
import re

from database import DatBase

db = DatBase()

router = Router()


@router.message(Command("start"))
async def start_handler(message):
    """Заносит пользователя в БД"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    chat_id = message.chat.id

    db.add_user(user_id, username, first_name, last_name, chat_id)

    await message.answer('Приветствую! Теперь вы зарегистрированы в боте.')

@router.message(Command("info"))
async def info_handler(message):
    """Проверяет есть ли пользовотель в БД и отправляет информацию о нем """
    chat_id = message.chat.id

    user = db.send_info(chat_id)

    if user:
        username = user[2] or 'неизвестно'
        first_name = user[3] or 'неизвестно'
        last_name = user[4] or 'неизвестно'

        await message.answer(f'Имя: {first_name}\nФамилия: {last_name}\nUsername: @{username}')
    else:
        await message.answer('Вы не зарегистрированы в боте.')

@router.message(Command("delete"))
async def delete_handler(message):
    """Удаляет пользователя из БД"""
    chat_id = message.chat.id

    db.remove_user(chat_id)

    await message.answer('Вы удалены из бота.')

@router.message(Command("spent", "earned", "s", "e"))
async def start(message):
    """Создаем записи о расходах и доходах"""
    cmd_variants = (('/spent', '/s', '!spent', '!s'), ('/earned', '/e', '!earned', '!e'))
    operation = '-' if message.text.startswith(cmd_variants[0]) else '+'

    value = message.text
    for i in cmd_variants:
        for j in i:
            value = value.replace(j, '').strip()

    if(len(value)):
        x = re.findall(r"\d+(?:.\d+)?", value)
        if(len(x)):
            value = float(x[0].replace(',', '.'))

            db.add_record(message.from_user.id, operation, value)

            if(operation == '-'):
                await message.reply("✏️ Запись о <u><b>расходе</b></u> успешно внесена!")
            else:
                await message.reply("✏️ Запись о <u><b>доходе</b></u> успешно внесена!")
        else:
            await message.reply("Не удалось определить сумму!")
    else:
        await message.reply("Не введена сумма!")

@router.message(Command("history", "h"))
async def start(message: types.Message):
    """Показываем историю расходов и доходов"""
    cmd_variants = ('/history', '/h', '!history', '!h')
    within_als = {
        "day": ('today', 'day', 'сегодня', 'день'),
        "month": ('month', 'месяц'),
        "year": ('year', 'год'),
    }

    cmd = message.text
    for r in cmd_variants:
        cmd = cmd.replace(r, '').strip()

    within = 'day'
    if(len(cmd)):
        for k in within_als:
            for als in within_als[k]:
                if(als == cmd):
                    within = k

    records = db.get_records(message.from_user.id, within)

    if(len(records)):
        answer = f"📄 История операций за {within_als[within][-1]}\n\n"

        for r in records:
            answer += "<b>" + ("➖ Расход" if not r[2] else "➕ Доход") + "</b>"
            answer += f" - {r[3]}"
            answer += f" <i>({r[4]})</i>\n"

        await message.reply(answer)
    else:
        await message.reply("Записей не обнаружено!")