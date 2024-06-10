import asyncio
import configparser
import logging
import pandas as pd
import random
import copy

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta

__AUTHOR__ = '@FirelGef'

__version__ = "1.1.3"

config = configparser.ConfigParser()  # создаём объекта парсера
config.read("config.ini")  # читаем конфиг

# Включение ведения журнала
logging.basicConfig(filename='bot.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Ваш токен, полученный от BotFather
TOKEN = config['BOT']['token']

# ID группы, в которую бот будет отправлять сообщения
GROUP_CHAT_ID = int(config['BOT']['groupChatID'])

# Список разрешенных пользователей
ALLOWED_USERS = list(map(int, config['BOT']['allowedUsers'].split(',')))

# таблица в гугле в формате: https://docs.google.com/spreadsheets/d/<TABLE_ID>/gviz/tq?tqx=out:csv&sheet=<LIST_NAME>
gurl = config['BOT']['googleSheets']

logger.info(f'token: {TOKEN}')
logger.info(f'chat_id: {GROUP_CHAT_ID}')
logger.info(f'allowed_users: {ALLOWED_USERS}')
logger.info(f'google_sheet: {gurl}')

dict_all_jobs = {}
all_users = {}
all_users_ids = {}
scheduler = AsyncIOScheduler()

bot = Bot(token=TOKEN)
dp = Dispatcher()

emojis = [
    "\U0001F600",  # grinning
    "\U0001F601",  # grin
    "\U0001F602",  # joy
    "\U0001F603",  # smiley
    "\U0001F604",  # smile
    "\U0001F605",  # sweat_smile
    "\U0001F606",  # laughing
    "\U0001F607",  # innocent
    "\U0001F609",  # wink
    "\U0001F60A",  # blush
    "\U0001F642",  # slightly_smiling_face
    "\U0001F643",  # upside_down_face
    "\U0001F60D",  # heart_eyes
    "\U0001F618",  # kissing_heart
    "\U0001F617",  # kissing
    "\U0001F619",  # kissing_smiling_eyes
    "\U0001F61A",  # kissing_closed_eyes
    "\U0001F60B",  # yum
    "\U0001F61B",  # stuck_out_tongue
    "\U0001F61C",  # stuck_out_tongue_winking_eye
    "\U0001F61D",  # stuck_out_tongue_closed_eyes
    "\U0001F911",  # money_mouth_face
    "\U0001F917",  # hugging_face
    "\U0001F913",  # nerd_face
    "\U0001F60E",  # sunglasses
    "\U0001F929",  # star_struck
    "\U0001F914",  # thinking
    "\U0001F92B",  # shushing_face
    "\U0001F928",  # face_with_raised_eyebrow
    "\U0001F610",  # neutral_face
    "\U0001F611",  # expressionless
    "\U0001F636",  # no_mouth
    "\U0001F60F",  # smirk
    "\U0001F612",  # unamused
    "\U0001F644",  # roll_eyes
    "\U0001F62C",  # grimacing
    "\U0001F925",  # lying_face
    "\U0001F60C",  # relieved
    "\U0001F614",  # pensive
    "\U0001F62A",  # sleepy
    "\U0001F924",  # drooling_face
    "\U0001F634",  # sleeping
    "\U0001F637",  # mask
    "\U0001F912",  # face_with_thermometer
    "\U0001F915",  # face_with_head_bandage
    "\U0001F922",  # nauseated_face
    "\U0001F92E",  # vomiting_face
    "\U0001F927",  # sneezing_face
    "\U0001F975",  # hot_face
    "\U0001F976",  # cold_face
    "\U0001F974",  # woozy_face
    "\U0001F635",  # dizzy_face
    "\U0001F92F",  # exploding_head
    "\U0001F920",  # cowboy_hat_face
    "\U0001F973",  # partying_face
    "\U0001F978",  # disguised_face
    "\U0001F60E",  # sunglasses
    "\U0001F913",  # nerd_face
    "\U0001F9D0",  # face_with_monocle
    "\U0001F615",  # confused
    "\U0001F61F",  # worried
    "\U0001F641",  # slightly_frowning_face
    "\U00002639",  # frowning_face
    "\U0001F62E",  # open_mouth
    "\U0001F62F",  # hushed
    "\U0001F632",  # astonished
    "\U0001F633",  # flushed
    "\U0001F97A",  # pleading_face
    "\U0001F626",  # frowning
    "\U0001F627",  # anguished
    "\U0001F628",  # fearful
    "\U0001F630",  # cold_sweat
    "\U0001F625",  # disappointed_relieved
    "\U0001F622",  # cry
    "\U0001F62D",  # sob
    "\U0001F631",  # scream
    "\U0001F616",  # confounded
    "\U0001F623",  # persevere
    "\U0001F61E",  # disappointed
    "\U0001F613",  # sweat
    "\U0001F629",  # weary
    "\U0001F62B",  # tired_face
    "\U0001F971",  # yawning_face
    "\U0001F624",  # triumph
    "\U0001F621",  # rage
    "\U0001F620",  # angry
    "\U0001F92C",  # cursing_face
    "\U0001F608",  # smiling_imp
    "\U0001F47F",  # imp
    "\U0001F480",  # skull
    "\U00002620",  # skull_and_crossbones
    "\U0001F4A9",  # hankey
    "\U0001F921",  # clown_face
    "\U0001F479",  # ogre
    "\U0001F47A",  # goblin
    "\U0001F47B",  # ghost
    "\U0001F47D",  # alien
    "\U0001F47E",  # space_invader
    "\U0001F916",  # robot
    "\U0001F383",  # jack_o_lantern
    "\U0001F63A",  # smiley_cat
    "\U0001F638",  # smile_cat
    "\U0001F639",  # joy_cat
    "\U0001F63B",  # heart_eyes_cat
    "\U0001F63C",  # smirk_cat
    "\U0001F63D",  # kissing_cat
    "\U0001F640",  # scream_cat
    "\U0001F63F",  # crying_cat_face
    "\U0001F63E",  # pouting_cat
    "\U0001F648",  # see_no_evil
    "\U0001F649",  # hear_no_evil
    "\U0001F64A",  # speak_no_evil
    "\U0001F48B",  # kiss
    "\U0001F48C",  # love_letter
    "\U0001F498",  # cupid
    "\U0001F49D",  # gift_heart
    "\U0001F496",  # sparkling_heart
    "\U0001F497",  # heartpulse
    "\U0001F493",  # heartbeat
    "\U0001F49E",  # revolving_hearts
    "\U0001F495",  # two_hearts
    "\U0001F49F",  # heart_decoration
    "\U00002763",  # heavy_heart_exclamation
    "\U0001F494",  # broken_heart
    "\U0001F9E4",  # heart_on_fire
    "\U0001F9E5",  # mending_heart
    "\U00002764",  # red_heart
    "\U0001F9E1",  # orange_heart
    "\U0001F49B",  # yellow_heart
    "\U0001F49A",  # green_heart
    "\U0001F499",  # blue_heart
    "\U0001F49C",  # purple_heart
    "\U0001F90E",  # brown_heart
    "\U0001F5A4",  # black_heart
    "\U0001F90D"  # white_heart
]


@dp.message(Command("start"))
async def start(message: types.Message):
    logger.info(f'start(): user: {message.from_user.id} chat_id: {message.chat.id}')
    if message.from_user.id not in ALLOWED_USERS:
        await message.reply('У вас нет доступа к использованию этого бота.')
        return
    admins = await bot.get_chat_administrators(GROUP_CHAT_ID)
    emojis_cp = copy.deepcopy(emojis)
    try:
        for admin in admins:
            emoji = random.choice(emojis_cp)
            emojis_cp.remove(emoji)
            all_users[f'@{admin.user.username}'] = {
                'id': admin.user.id,
                'FName': admin.user.first_name,
                'LName': admin.user.last_name,
                'emoji': emoji,
                'custom_title': admin.custom_title
            }
            all_users_ids[admin.user.id] = {
                'UTag': f'@{admin.user.username}',
                'FName': admin.user.first_name,
                'LName': admin.user.last_name,
                'emoji': emoji,
                'custom_title': admin.custom_title
            }
            log_info = "\n".join(
                [
                    f"User ID: {admin.user.id}\n"
                    f"First Name: {admin.user.first_name}\n"
                    f"Last Name: {admin.user.last_name}\n"
                    f"Username: @{admin.user.username}\n"
                    f"Status: {admin.status}\n"
                    f'Custom Title: {admin.custom_title}\n'
                    "-----"
                ]
            )
            logger.info(log_info)
        await message.reply('Бот запущен!')
    except Exception as err:
        logger.error(f'start(): something wrong! Error: {err}')
        await message.reply(f'Что-то пошло не так! Обратитесь к {__AUTHOR__} для решения проблемы.')


@dp.message(Command("call_user"))
async def call_user(message: types.Message):
    logger.info(f'call_user(): {message.from_user.id}')
    if message.from_user.id not in ALLOWED_USERS:
        await message.reply('У вас нет доступа к использованию этого бота.')
        return
    args = message.text.split()
    if len(args) < 3:
        logger.warning(f'len(args) < 3: {args}')
        await message.reply('Использование: /call_user @<TGName> <время в формате HH:MM> [сообщение]')
        return
    nick = args[1]
    try:
        if nick.startswith('@'):
            user_id = all_users[nick]['id']
            user_name = nick
        elif nick.isdigit():
            user_name = all_users_ids[int(nick)]['UTag']
            user_id = nick
        else:
            logger.warning(
                f'Ошибка в ID пользователя: {nick}. ID должен начинаться с символа "@" или быть id пользователя')
            await message.reply(
                f'Ошибка в ID пользователя: {nick}. ID должен начинаться с символа "@" или быть id пользователя')
            return
    except:
        logger.warning('Неизвестное имя пользователя')
        await message.reply('Неизвестное имя пользователя')
        return

    call_time = args[2]
    custom_message = ' '.join(args[3:]) if len(args) > 3 else 'Время пришло!'
    try:
        call_time = datetime.strptime(call_time, '%H:%M').time()
        now = datetime.now()
        call_datetime = datetime.combine(now, call_time)
        if call_datetime < now:
            call_datetime += timedelta(days=1)

        trigger = DateTrigger(run_date=call_datetime)
        job = scheduler.add_job(send_message, trigger, args=[user_name, user_id, custom_message])
        await message.reply(f'Пользователь {user_name[1:]} будет вызван в {call_datetime.strftime("%Y-%m-%d %H:%M")}')
        dict_all_jobs[f'{nick}'] = {'time': f'{call_datetime.strftime("%Y-%m-%d %H:%M")}', 'id': f'{job.id}'}
    except ValueError:
        await message.reply(f'Неправильный формат времени: {call_time}')
        await message.reply('Неправильный формат времени. Используйте HH:MM.')


@dp.message(Command("start_timer"))
async def start_timer(message: types.Message):
    logger.info(f'start_timer(): {message.from_user.id}')
    if message.from_user.id not in ALLOWED_USERS:
        await message.reply('У вас нет доступа к использованию этого бота.')
        return
    args = message.text.split()
    df = pd.read_csv(gurl)
    all_line = len(df.values)
    line_count = 0
    for val in df.values:
        try:
            user_id, title, nick, stime, = val[0], val[1], val[2], val[3]
            if not isinstance(nick, str) or not isinstance(stime, str) or not isinstance(user_id, int):
                logger.warning(
                    f'ID {user_id} {type(user_id)} пользователя или Time {stime} {type(stime)} не заполнено. {val[0]}, {val[1]}, {val[2]}, {val[3]}')
                # await message.reply(f'Nick, ID пользователя или Time не заполнено.')
                continue
            user_id = int(user_id)
            logger.info(f'start_timer(): {message.from_user.id}: user_name: {nick}, time: {stime}')

            call_time = datetime.strptime(stime, '%H:%M').time()
            now = datetime.now()
            call_datetime = datetime.combine(now, call_time)
            if call_datetime < now:
                call_datetime += timedelta(days=1)

            trigger = DateTrigger(run_date=call_datetime)
            job = scheduler.add_job(send_message, trigger, args=[title, user_id, 'Вестник!'])
            dict_all_jobs[f'{user_id}'] = {'time': f'{call_datetime.strftime("%Y-%m-%d %H:%M")}', 'id': f'{job.id}'}
            line_count += 1
            # await message.answer(f'Пользователь {title} будет вызван в {call_datetime.strftime("%Y-%m-%d %H:%M")}')
        except ValueError:
            await message.reply(f'Неправильный формат времени: {stime}. Используйте HH:MM.')
    await message.reply(f'{line_count}/{all_line} призывов запланировано.')


@dp.message(Command("all_jobs"))
async def all_jobs(message: types.Message):
    logger.info(f'all_jobs(): {message.from_user.id}')
    if message.from_user.id not in ALLOWED_USERS:
        await message.reply('У вас нет доступа к использованию этого бота.')
        return
    await message.reply(f'{dict_all_jobs}')


@dp.message(Command("remove_job"))
async def remove_job(message: types.Message):
    logger.info(f'remove_job(): {message.from_user.id}')
    if message.from_user.id not in ALLOWED_USERS:
        await message.reply('У вас нет доступа к использованию этого бота.')
        return
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply(f'Не указан ID пользователя! Укажите пользователя в формате: @<TGName>')
            return
        user_name = args[1]
        scheduler.remove_job(dict_all_jobs[user_name]['id'])
        logger.info(f'Job with ID {user_name} has been removed.')
        del (dict_all_jobs[user_name])
    except:
        await message.reply(f'Задача не обнаружена: {user_name}')


@dp.message(Command("remove_all_jobs"))
async def remove_all_jobs(message: types.Message):
    logger.info(f'remove_all_jobs(): {message.from_user.id}')
    if message.from_user.id not in ALLOWED_USERS:
        await message.reply('У вас нет доступа к использованию этого бота.')
        return
    users_names = [user for user in dict_all_jobs.keys()]
    for user_name in users_names:
        try:
            scheduler.remove_job(dict_all_jobs[user_name]['id'])
            logger.info(f'Job with ID {user_name} has been removed.')
            del (dict_all_jobs[user_name])
        except:
            del (dict_all_jobs[user_name])


@dp.message(Command("call_all"))
async def call_all(message: types.Message):
    logger.info(f'call_all(): {message.from_user.id}')
    if message.from_user.id not in ALLOWED_USERS:
        await message.reply('У вас нет доступа к использованию этого бота.')
        return
    args = message.text.split()
    if len(args) > 1:
        user_message = args[1:]
    else:
        user_message = None
    custom_message = ' '.join(user_message) if user_message else 'Всем внимание!'
    count = 0
    msg = ''
    for user_name in all_users_ids.keys():
        user_id = user_name
        user_emoji = all_users_ids[user_name]['emoji']
        msg += f'<a href="tg://user?id={user_id}">{user_emoji}</a> '
        count += 1
        if count == 8:
            msg += custom_message
            await bot.send_message(chat_id=GROUP_CHAT_ID, text=msg, parse_mode='HTML')
            count = 0
            msg = ''
    if msg:
        msg += custom_message
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=msg, parse_mode='HTML')


@dp.message(Command("get_all"))
async def get_all(message: types.Message):
    logger.info(f'get_all(): {message.from_user.id}')
    if message.from_user.id not in ALLOWED_USERS:
        await message.reply('У вас нет доступа к использованию этого бота.')
        return
    msg = ''
    for uid in all_users_ids.keys():
        tg_name = all_users_ids[uid]['UTag']
        nick = all_users_ids[uid]['custom_title']
        msg += f'ID: {uid}\tTGName: {tg_name}\tGame Nick: {nick}\n'
    if len(all_users_ids.keys()):
        await message.answer(msg)
    else:
        await message.reply(
            f'Нет записей о пользователях, выполните команду /start. Если ошибка повторяется обратитесь к {__AUTHOR__}')


@dp.message(Command("get_new"))
async def get_new(message: types.Message):
    logger.info(f'get_new(): {message.from_user.id}')
    if message.from_user.id not in ALLOWED_USERS:
        await message.reply('У вас нет доступа к использованию этого бота.')
        return
    all_ids = all_users_ids.keys()
    df = pd.read_csv(gurl)
    msg = ''
    table_user_ids = []
    for val in df.values:
        user_id = val[0]
        if not isinstance(user_id, int):
            logger.warning(
                f'ID {user_id} {type(user_id)} пользователя не заполнено. {val[0]}, {val[1]}, {val[2]}, {val[3]}')
            continue
        table_user_ids.append(user_id)
    for uid in all_ids:
        if uid not in table_user_ids:
            nick = all_users_ids[uid]['custom_title']
            tg_name = all_users_ids[uid]['UTag']
            msg += f'ID: {uid}\tGame Nick: {nick}\tTGName: {tg_name}\n'
    if msg:
        await message.answer(msg)
    elif not all_ids:
        await message.reply(
            f'Нет записей о пользователях, выполните команду /start. Если ошибка повторяется обратитесь к {__AUTHOR__}')
    else:
        await message.answer('Новых пользователей не обнаружено. Проверьте всем ли выданы права admin.')


@dp.message(Command("help"))
async def help_command(message: types.Message):
    logger.info(f'help(): {message.from_user.id}')
    if message.from_user.id not in ALLOWED_USERS:
        await message.reply('У вас нет доступа к использованию этого бота.')
        return
    help_text = (
        "=====================================================================================\n"
        "Доступные команды:\n\n"
        "- start - Запустить бота и сформировать информацию по пользователям\n\n"
        "- get_all - получить список доступных для призыва пользователей\n\n"
        "- get_new - получить список пользователей, которые не обнаружены в таблице\n\n"
        "- call_user - Вызвать пользователя в указанное время\n"
        "        Использование: [@<TGName> или user_id] [время в формате HH:MM] [сообщение]\n\n"
        "- call_all - Вызвать всех пользователей с ролью админ\n\n"
        "- start_timer - Завести таймер на основе таблицы\n\n"
        "- all_jobs - Вывести все запланированные задачи\n\n"
        "- remove_job - Удаляет задачу\n"
        "        Принимает 1 параметр: user_name: Тег телеграмма в формате @<TGName> или user_id\n\n"
        "- remove_all_jobs - Удаляет  все запланированные задачи\n\n"
        "- help - Показать доступные команды\n\n"
        "=====================================================================================\n"
    )

    await message.reply(help_text)


async def send_message(nick, user_id, text):
    message = f'<a href="tg://user?id={user_id}">{nick}</a> {text}'
    await bot.send_message(chat_id=GROUP_CHAT_ID, text=message, parse_mode='HTML')


async def main():
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
