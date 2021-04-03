import os
import telebot, pymysql, time
from telebot import types

#token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot('912680602:AAFuJ7VF3CuxO2_giada4gqGP_dwfLqkp5c')

con = pymysql.connect(host="us-cdbr-east-03.cleardb.com", user="b40f50224688c7", passwd="d01ea3eb", db='heroku_80fffc474875cce')
cur = con.cursor()
timer_con = time.time()


def check_timer_con():
    global con, cur, timer_con
    if time.time() - timer_con > 600:
        print(f'Срок действия курсора вышел ({int(time.time() - timer_con)}сек.)')
        con = pymysql.connect(host="us-cdbr-east-03.cleardb.com",
                              user="b40f50224688c7", passwd="d01ea3eb",
                              db='heroku_80fffc474875cce')
        cur = con.cursor()
        timer_con = time.time()


def create_markup(keyboard, mod=0):
    pass


@bot.message_handler(commands=['start', 'help', 'reload'])
def send_help(message):
    if message.text == '/reload':
        bot.send_message(message.chat.id, 'Сейчас будет специально допущенна ошибка деления на 0, из за чего сервер падёт и после этого через 1-2 минуты перезагрузиться')
        print(1/0)
    elif message.text == '/help' or message.text == 'start':
        markup = types.ReplyKeyboardMarkup()
        item_btn1 = types.KeyboardButton('Правила')
        item_btn2 = types.KeyboardButton('все данные из test1')
        markup.row(item_btn1, item_btn2)

        bot.send_message(message.chat.id, '''напиши "добавить : <int>;<int>;<str>", чтоб добавить новые данные в таблицу test1
    напиши "удалить : <int>", чтоб удалить выбранную строку из таблицы test1''',
                             reply_markup=markup)


@bot.message_handler(content_types=['text'])
def echo_all(message):
    print(f'Новое сообщение от {message.chat.first_name} {message.chat.last_name}: {message.text}')
    text = 'Сори я не понимаю тебя, пльзуйся кнопками'
    try:
        if message.text == 'Информация':
            text = 'Информация'
        elif message.text == 'Правила':
            text = 'В отличие от других шопов, я НЕСУ ответственность за неудачный реф или вбив, будет перезаказ!!! /help'
        elif message.text == 'Расценки':
            text = 'Цена не высока и варируется от кол-ва вашего заказа (об этом более подробно сказано в разделе "Информация") от 30 до 25%'
        elif message.text == 'все данные из test1':
            check_timer_con()
            text = ''
            cur.execute('''SELECT DISTINCT * FROM test1''')
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
        text = 'что-то пошло не так. Скорее всего вы подали не правильные данные, попробуйте ещё раз'
        check_timer_con()
    bot.send_message(message.chat.id, text)


bot.polling()

