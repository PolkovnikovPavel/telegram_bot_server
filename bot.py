import os
import random

import telebot, pymysql, time, requests
from telebot import types
from textes import *

token = os.environ['TELEGRAM_TOKEN']
#token = 'secret'
my_login = os.environ['MY_LOGIN']
#my_login = 'secret'
api_access_token = os.environ['API_ACCESS_TOKEN']
#api_access_token = 'secret'
passwd_db = os.environ['PASSWD_DB']
#passwd_db = 'secret'

abc = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'V', 'X', 'Y', 'Z']


bot = telebot.TeleBot(token)

con = pymysql.connect(host="us-cdbr-east-03.cleardb.com", user="b40f50224688c7", passwd=passwd_db, db='heroku_80fffc474875cce')
cur = con.cursor()
timer_con = time.time()


def generate_special_code_mini(message):
    r1 = random.choice(abc)
    r2 = random.choice(abc)
    r3 = random.choice(abc)
    r4 = random.choice(abc)
    r5 = random.choice(abc)
    cod = f'5{r1}{str(message.chat.id)[-3:]}{str(message.chat.id)[:-3]}{r2}{r3}{r4}{r5}0'
    return cod


def generate_special_code(message):
    r1 = random.choice(abc)
    r2 = random.choice(abc)
    r3 = random.choice(abc)
    r4 = random.choice(abc)
    r5 = random.choice(abc)
    cod = f'5{r1}{str(message.chat.id)[-3:]}{str(message.chat.id)[:-3]}{r2}{r3}{r4}{r5}1'
    return cod


def generate_pay_code(message):
    num = str(time.time())[-5:]
    r = random.choice(range(1000, 9999))
    return str(r) + str(message.chat.id) + num


def send_msg_to_comment(text):
    bot.send_message('@Real_money_otzivi', text)


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
    check_timer_con()
    if not mod:
        cur.execute(f'''SELECT DISTINCT * FROM users
        WHERE id = {message.chat.id}''')
        result = cur.fetchall()
    else:
        result = False

    if not result:
        pay_code = generate_pay_code(message)
        inquiry = f"""INSERT INTO users
VALUES ({message.chat.id}, '', '', '', '', '{pay_code}', '0', 0, 0, '80', '0', 0, 0)"""
        cur.execute(inquiry)
        con.commit()
        print(f'добавлен новый пользователь, id = {message.chat.id}, зовут {message.chat.first_name} {message.chat.last_name}')
        bot.send_message(message.chat.id, text_1,
            reply_markup=create_markup([[button_1]]))


def create_mini_invite_code(message):
    new_mini_invite_code = generate_special_code_mini(message)
    check_timer_con()
    inquiry = f"""UPDATE users
    SET type_menu = 2, mini_invite_code = '{new_mini_invite_code}'
        WHERE id = '{message.chat.id}'"""
    cur.execute(inquiry)
    con.commit()
    bot.send_message(message.chat.id, text_29)
    bot.send_message(message.chat.id, f'Ваш новый пригласительный код "{new_mini_invite_code}" (ковычки не надо)')


def create_invite_code(message, data_of_person):
    check_timer_con()
    if float(data_of_person[10]) < 50:
        bot.send_message(message.chat.id, text_31)
        return False
    new_balance = float(data_of_person[10]) - 50
    new_invite_code = generate_special_code(message)
    if data_of_person[4] != '0':
        cur.execute(f"""SELECT DISTINCT * FROM users
            WHERE invite_code = '{data_of_person[4]}' OR mini_invite_code = '{data_of_person[4]}'""")
        result = cur.fetchall()[0]
        if data_of_person[4][0] == '5':
            if result[12] == 0:
                num_phone = result[3]
                if data_of_person[4][-1] == '1':
                    summ = 50 * float(result[9])
                else:
                    summ = 50 * float(result[9]) / 2

                print(f'Тут должен быть перевод {summ} руб. на номер {num_phone}')
                bot.send_message(message.chat.id, f'Тут должен быть перевод {summ} руб. на номер {num_phone}')

                inquiry = f"""UPDATE users
        SET balance = '{new_balance}', invite_code = '{new_invite_code}'
            WHERE id = '{message.chat.id}'"""
                cur.execute(inquiry)
                con.commit()

                inquiry = f"""UPDATE users
        SET amount_earned = '{result[6] + summ}'
            WHERE id = '{result[0]}'"""
                cur.execute(inquiry)
                con.commit()
                bot.send_message(message.chat.id, text_32)
                return new_invite_code
            else:
                pass   # тут всё тоже самое, но перевод на карту
        elif data_of_person[4][0] == '1':
            pass  # это на тот момент, когда, оплата станет 100 рублей, а не 50
    else:
        inquiry = f"""UPDATE users
        SET balance = '{new_balance}', invite_code = '{new_invite_code}'
            WHERE id = '{message.chat.id}'"""
        cur.execute(inquiry)
        con.commit()
        bot.send_message(message.chat.id, text_32)
        return new_invite_code


def acquaintance_with_the_bot(message):
    markup = create_markup([['Отзывы', 'https://t.me/joinchat/GP4M-utAjARjYTBi'],
                            ['Общий чат', 'https://t.me/joinchat/VGR26kXHtd03NGM6'],
                            ['продвижение в соцсетях', 'https://t.me/joinchat/eJCM8XbEOwA1MDky']], mod=1)

    bot.send_message(message.chat.id, text_5, reply_markup=markup)
    change_type_menu(message, 2)


def check_who_invited_me(who_invited_me):
    check_timer_con()
    cur.execute(f"""SELECT DISTINCT * FROM users
        WHERE invite_code = '{who_invited_me}' OR mini_invite_code = '{who_invited_me}'""")
    result = cur.fetchall()
    if not result:
        return False
    return True


def payment_history_last(my_login, api_access_token, rows_num):
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + api_access_token
    parameters = {'rows': rows_num, 'nextTxnId': '', 'nextTxnDate': ''}
    h = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + my_login + '/payments', params = parameters)
    return h.json()


def find_new_transfer(data_of_person):
    plus = 0
    payments = payment_history_last(my_login, api_access_token, '50')
    for payment in payments['data']:
        if payment['comment'] == data_of_person[5] and payment['type'] == 'IN' and payment['status'] == 'SUCCESS':
            plus = payment['sum']['amount']
    return plus


def check_num_phone(num_phone):
    rez = ''
    if len(num_phone) == 11 and num_phone[0] == '8':
        rez = f'7{num_phone[1:]}'
    return rez


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


def check_timer_con(mod=0):
    if mod == 1:
        create_con()
    if time.time() - timer_con > 60:
        create_con()


def change_type_menu(message, new_type):
    check_timer_con()
    inquiry = f"""UPDATE users
    SET type_menu = {new_type}
        WHERE id = '{message.chat.id}'"""
    cur.execute(inquiry)
    con.commit()


def create_markup(keyboard, mod=0):
    if mod == 0:
        markup = types.ReplyKeyboardMarkup()
        for line in keyboard:
            items = []
            for key in line:
                items.append(types.KeyboardButton(key))
            markup.row(*items)
    else:
        markup = types.InlineKeyboardMarkup()
        for cell in keyboard:
            if type(cell) is str or len(cell) == 1:
                return None
            btn = types.InlineKeyboardButton(text=cell[0], url=cell[1])
            markup.add(btn)
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


@bot.channel_post_handler(content_types=['text'])
def process_channel_message(message):
    pass


@bot.message_handler(content_types=['text'])
def echo_all(message):
    print(f'Новое сообщение от {message.chat.first_name} {message.chat.last_name}: {message.text}')
    try:
        data_of_person = get_data_of_person(message)[0]
    except Exception:
        text = 'что-то пошло не так. Скорее всего потеряно соединение с сервером MySQL во время запроса. Попробуйте ещё раз, а мы пока наладим соединение'
        check_timer_con(1)
        bot.send_message(message.chat.id, text)
        return

    text = 'Сори я не понимаю тебя, пльзуйся кнопками'
    markup = None
    try:
        if data_of_person[11] == 0:
            if message.text != button_1:
                if check_who_invited_me(message.text):
                    set_who_invited_me(message, message.text)
                    text = text_3
                    markup = create_markup([[button_2]])

                    inquiry = f"""UPDATE users
        SET number_invitees = '{data_of_person[7] + 1}'
            WHERE invite_code = '{message.text}' OR mini_invite_code = '{message.text}'"""
                    cur.execute(inquiry)
                    con.commit()
                else:
                    text = text_2
                    markup = create_markup([[button_1]])
            else:
                set_who_invited_me(message, '0')
                text = text_3
                markup = create_markup([[button_2]])

        elif data_of_person[11] == 1:
            if message.text == button_2:
                acquaintance_with_the_bot(message)
                text = text_6
                markup = create_markup(buttons_main_menu)
            else:
                text = text_4
                markup = create_markup([[button_2]])
        elif data_of_person[11] == 2:
            if message.text == button_3:
                text = text_7
                markup = create_markup(buttons_main_menu)
            elif message.text == button_8:
                text = text_8
                markup = create_markup(buttons_main_menu)
            elif message.text == button_6:
                markup = create_markup([['Отзывы', 'https://t.me/joinchat/WQxUOA1TwmQ0Yjky']], mod=1)
                bot.send_message(message.chat.id, text_10, reply_markup=markup)
                text = text_9
                markup = create_markup(buttons_comment_menu_1)
                change_type_menu(message, 3)
            elif message.text == button_4:
                change_type_menu(message, 5)
                bot.send_message(message.chat.id, text_14)
                bot.send_message(message.chat.id, f'{data_of_person[10]} Руб.')
                text = text_16
                markup = create_markup([[button_11], [button_12], [button_back]])
            elif message.text == button_5:
                text = f'{text_20} {data_of_person[6]} Руб. И пригласили {data_of_person[7]} человек'
                markup = create_markup(buttons_main_menu)
            elif message.text == button_13:
                inquiry = f"""UPDATE users
                SET balance = '{float(data_of_person[10]) + 15}'
                    WHERE id = '{message.chat.id}'"""
                cur.execute(inquiry)
                con.commit()
                text = 'Это временно (баланс +15 руб)'

            elif message.text == button_7:
                if data_of_person[3] == '':
                    change_type_menu(message, 7)
                    text = text_21
                    markup = markup = create_markup([[button_14], [button_15], [button_back]])
                else:
                    if data_of_person[1] == '' and data_of_person[2] == '':
                        change_type_menu(message, 10)
                        text = text_26
                        markup = markup = create_markup([[button_17], [button_18], [button_back]])
                    elif data_of_person[1] == '' and data_of_person[2] != '':
                        bot.send_message(message.chat.id, f'{text_33} "{data_of_person[2]}" (ковычки не надо)')
                        change_type_menu(message, 9)
                        text = text_34
                        markup = markup = create_markup([[button_16], [button_back]])
                    else:
                        text = text_30 + f' "{data_of_person[1]}" (ковычки не надо)'
                        markup = create_markup(buttons_main_menu)
                        change_type_menu(message, 2)
            else:
                text = 'В разработке'
                markup = create_markup(buttons_main_menu)

        elif data_of_person[11] == 7:
            if message.text == button_back:
                text = text_6
                markup = create_markup(buttons_main_menu)
                change_type_menu(message, 2)
            elif message.text == button_14:
                change_type_menu(message, 8)
                text = text_22
                markup = markup = create_markup([[button_back]])
            elif message.text == button_15:
                text = 'В разработке'
                markup = markup = create_markup([[button_14], [button_15], [button_back]])

        elif data_of_person[11] == 8:
            if message.text == button_back:
                change_type_menu(message, 7)
                text = text_21
                markup = markup = create_markup([[button_14], [button_15], [button_back]])
            else:
                num_phone = check_num_phone(message.text)
                if num_phone:
                    check_timer_con()
                    inquiry = f"""UPDATE users
    SET type_menu = 9, num_phone = '{num_phone}'
        WHERE id = '{message.chat.id}'"""
                    cur.execute(inquiry)
                    con.commit()
                    bot.send_message(message.chat.id, text_25)
                    text = text_26
                    markup = markup = create_markup([[button_16], [button_back]])
                else:
                    text = text_24
                    markup = markup = create_markup([[button_back]])

        elif data_of_person[11] == 9:
            if message.text == button_back:
                text = text_6
                markup = create_markup(buttons_main_menu)
                change_type_menu(message, 2)
            elif message.text == button_16:
                if data_of_person[1] == '' and data_of_person[2] == '':
                    change_type_menu(message, 10)
                    text = text_27
                    markup = markup = create_markup([[button_17], [button_18], [button_back]])
                elif data_of_person[1] == '' and data_of_person[2] != '':
                    new_invite_code = create_invite_code(message, data_of_person)
                    if new_invite_code:
                        text = text_30 + f' "{new_invite_code}" (ковычки не надо)'
                        markup = create_markup(buttons_main_menu)
                        change_type_menu(message, 2)
                    else:
                        text = text_6
                        markup = create_markup(buttons_main_menu)
                        change_type_menu(message, 2)
                else:
                    text = text_28
                    markup = markup = create_markup([[button_back]])

        elif data_of_person[11] == 10:
            if message.text == button_back:
                change_type_menu(message, 9)
                text = text_26
                markup = markup = create_markup([[button_16], [button_back]])
            elif message.text == button_17:
                create_mini_invite_code(message)   # тип меню 2
                text = text_6
                markup = create_markup(buttons_main_menu)
            elif message.text == button_18:
                if create_invite_code(message, data_of_person):
                    text = text_6
                    markup = create_markup(buttons_main_menu)
                    change_type_menu(message, 2)
                else:
                    text = text_27
                    markup = markup = create_markup([[button_17], [button_18], [button_back]])



        elif data_of_person[11] == 5:
            if message.text == button_back:
                text = text_6
                markup = create_markup(buttons_main_menu)
                change_type_menu(message, 2)
            elif message.text == button_11:
                change_type_menu(message, 6)
                bot.send_message(message.chat.id, f'{text_15} "{data_of_person[5]}" (ковычки не надо)')
                text = text_16
                markup = create_markup([[button_10], [button_back]])

            elif message.text == button_12:
                text = 'В разработке'
                markup = create_markup([[button_11], [button_12], [button_back]])

        elif data_of_person[11] == 6:
            if message.text == button_back:
                change_type_menu(message, 5)
                bot.send_message(message.chat.id, text_14)
                bot.send_message(message.chat.id, f'{data_of_person[10]} Руб.')
                text = text_16
                markup = create_markup([[button_11], [button_12], [button_back]])
            elif message.text == button_10:
                plus = find_new_transfer(data_of_person)
                if plus:
                    new_balance = float(data_of_person[10]) + plus
                    bot.send_message(message.chat.id, f'{text_18} {new_balance} Руб.')

                    new_pay_code = generate_pay_code(message)

                    check_timer_con()
                    inquiry = f"""UPDATE users
    SET type_menu = 2, balance = '{new_balance}', pay_code = '{new_pay_code}'
        WHERE id = '{message.chat.id}'"""
                    cur.execute(inquiry)
                    con.commit()
                    text = text_19
                    markup = create_markup(buttons_main_menu)
                else:
                    text = text_17
                    markup = create_markup([[button_10], [button_back]])


        elif data_of_person[11] == 3:
            if message.text == button_9:
                if time.time() - data_of_person[8] > 6 * 60 * 60:   # 6 часов
                    change_type_menu(message, 4)
                    text = text_12
                    markup = create_markup([[button_back]])
                else:
                    text = text_11
                    markup = create_markup(buttons_comment_menu_1)
            elif message.text == button_back:
                text = text_6
                markup = create_markup(buttons_main_menu)
                change_type_menu(message, 2)

        elif data_of_person[11] == 4:
            if message.text == button_back:
                text = text_9
                markup = create_markup(buttons_comment_menu_1)
                change_type_menu(message, 3)
            else:
                send_msg_to_comment(message.text)
                text = text_13
                markup = create_markup(buttons_comment_menu_1)
                check_timer_con()
                inquiry = f"""UPDATE users
    SET time_last_comment = {int(time.time())}, type_menu = 3
        WHERE id = '{message.chat.id}'"""
                cur.execute(inquiry)
                con.commit()


        if message.text == 'все данные из test1':
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
        elif 'отзыв: ' in message.text:
            text = message.text.split('отзыв: ')[-1]
            send_msg_to_comment(text)


    except Exception:
        text = 'что-то пошло не так. Попробуйте ещё раз, а мы пока всё наладим'
        check_timer_con(1)
    if markup:
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text)


bot.polling()

