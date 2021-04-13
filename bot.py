import os
import telebot, pymysql, time
from telebot import types
from textes import *

#token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot('912680602:AAFuJ7VF3CuxO2_giada4gqGP_dwfLqkp5c')

con = pymysql.connect(host="us-cdbr-east-03.cleardb.com", user="b40f50224688c7", passwd="d01ea3eb", db='heroku_80fffc474875cce')
cur = con.cursor()
timer_con = time.time()


def generate_pay_code(message):
    num = str(time.time())[-5:]
    return str(message.chat.id) + num


def get_data_of_person(message):
    check_timer_con()
    cur.execute(f'''SELECT DISTINCT * FROM users
    WHERE id = {message.chat.id}''')
    result = cur.fetchall()
    if not result:
        create_user(message, True)
        cur.execute(f'''SELECT DISTINCT * FROM users
    WHERE id = {message.chat.id}''')
        result = cur.fetchall()
    return result


def create_user(message, mod=False):
    if not mod:
        cur.execute(f'''SELECT DISTINCT * FROM users
        WHERE id = {message.chat.id}''')
        result = cur.fetchall()
    else:
        result = False

    if not result:
        pay_code = generate_pay_code(message)
        inquiry = f"""INSERT INTO users
VALUES ({message.chat.id}, '', '', '', '', '{pay_code}', '0', 0, 0, '80', '0', 0)"""
        cur.execute(inquiry)
        con.commit()
        print(f'добавлен новый пользователь, id = {message.chat.id}, зовут {message.chat.first_name} {message.chat.last_name}')
        bot.send_message(message.chat.id, text_1,
            reply_markup=create_markup([[button_1]]))


def check_who_invited_me(who_invited_me):
    check_timer_con()
    cur.execute(f"""SELECT DISTINCT * FROM users
        WHERE who_invited_me = '{who_invited_me}'""")
    result = cur.fetchall()
    if not result:
        return False
    return True


def set_who_invited_me(message, who_invited_me):
    inquiry = f"""UPDATE users
            SET who_invited_me = '{who_invited_me}', type_menu = 1
                WHERE id = '{message.chat.id}'"""
    cur.execute(inquiry)
    con.commit()


def create_con():
    global con, cur, timer_con
    text = f'Срок действия курсора вышел ({int(time.time() - timer_con)}сек.)'
    print(text)
    con = pymysql.connect(host="us-cdbr-east-03.cleardb.com",
                          user="b40f50224688c7", passwd="d01ea3eb",
                          db='heroku_80fffc474875cce')
    cur = con.cursor()
    timer_con = time.time()

    inquiry = f"""INSERT INTO test1
                        VALUES ({int(time.time())}, {1000}, '{text}')"""
    cur.execute(inquiry)
    con.commit()


def check_timer_con(mod=0):
    if mod == 1:
        create_con()
    if time.time() - timer_con > 60:
        create_con()


def create_markup(keyboard, mod=0):
    markup = types.ReplyKeyboardMarkup()
    for line in keyboard:
        items = []
        for key in line:
            items.append(types.KeyboardButton(key))
        markup.row(*items)
    return markup


@bot.message_handler(commands=['start', 'help', 'reload_server_652431', 'reset_con'])
def send_help(message):
    if message.text == '/reload_server_652431':
        bot.send_message(message.chat.id, 'Сейчас будет специально допущенна ошибка деления на 0, из за чего сервер падёт и после этого через 1-2 минуты перезагрузиться')
        print(1/0)
    elif message.text == '/reset_con':
        check_timer_con(1)
        bot.send_message(message.chat.id,
    'Переподключение к базе данных прошло успешно. И теперь в test1 есть об этом данные')

    elif message.text == '/start':
        create_user(message)

    elif message.text == '/help':
        markup = create_markup([['Информация', 'Правила'], ['все данные из test1', 'все данные из users']])

        bot.send_message(message.chat.id, '''напиши "добавить : <int>;<int>;<str>", чтоб добавить новые данные в таблицу test1
    напиши "удалить : <int>", чтоб удалить выбранную строку из таблицы test1''',
                             reply_markup=markup)


@bot.message_handler(content_types=['text'])
def echo_all(message):
    print(f'Новое сообщение от {message.chat.first_name} {message.chat.last_name}: {message.text}')
    data_of_person = get_data_of_person(message)[0]
    text = 'Сори я не понимаю тебя, пльзуйся кнопками'
    markup = None
    try:
        if data_of_person[11] == 0:
            if message.text != button_1:
                if check_who_invited_me(message.text):
                    set_who_invited_me(message, message.text)
                    text = text_3
                    markup = create_markup([[button_2]])
                else:
                    text = text_2
                    markup = create_markup([[button_1]])
            else:
                set_who_invited_me(message, '0')
                text = text_3
                markup = create_markup([[button_2]])

        if data_of_person[11] == 1:
            if message.text == button_2:
                pass   # перейти в штатный режим
            else:
                text = text_4
                markup = create_markup([[button_2]])

        elif message.text == 'все данные из test1':
            check_timer_con()
            text = ''
            cur.execute('''SELECT DISTINCT * FROM test1''')
            results = cur.fetchall()
            for items in results:
                text += str(items) + '\n'
        elif message.text == 'все данные из users':
            check_timer_con()
            text = ''
            cur.execute('''SELECT DISTINCT * FROM users''')
            results = cur.fetchall()
            for items in results:
                text += str(items) + '\n'
        elif 'добавить :' in message.text:
            check_timer_con()
            num1, num2, str1 = message.text.split('добавить :')[-1].split(';')
            inquiry = f"""INSERT INTO test1
                               VALUES ({int(num1)}, {int(num2)}, '{str1}')"""
            cur.execute(inquiry)
            con.commit()
            text = 'в test1 успешно добавлены данные, теперь можно их посмотреть'
        elif 'удалить :' in message.text:
            check_timer_con()
            id = int(message.text.split('удалить :')[-1])
            cur.execute(f"""SELECT DISTINCT * FROM test1
                    WHERE id = {id}""")
            results = cur.fetchall()
            if results:
                inquiry = f"""DELETE FROM test1
                    WHERE id = {id}"""
                cur.execute(inquiry)
                con.commit()
                text = 'строка с данными успещно была удалена'
            else:
                text = f'тут нечего удалять, нету ни одной записи, в которой id = {id}'

    except Exception:
        text = 'что-то пошло не так. Скорее всего потеряно соединение с сервером MySQL во время запроса. Попробуйте ещё раз, а мы пока наладим соединение'
        check_timer_con(1)
    if markup:
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text)


bot.polling()

