import os
import telebot
#from telebot import types

#token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot('912680602:AAFuJ7VF3CuxO2_giada4gqGP_dwfLqkp5c')


def create_markup(keyboard, mod=0):
    pass

@bot.message_handler(commands=['start', 'help'])
def send_help(message):
    bot.send_message(message.chat.id, 'тут типо помощь')


@bot.message_handler(content_types=['text'])
def echo_all(message):
    print(message.text)
    text = 'Сори я не понимаю тебя, пльзуйся кнопками'
    if message.text == 'Информация':
        text = 'Информация'
    elif message.text == 'Правила':
        text = 'В отличие от других шопов, я НЕСУ ответственность за неудачный реф или вбив, будет перезаказ!!!'
    elif message.text == 'Расценки':
        text = 'Цена не высока и варируется от кол-ва вашего заказа (об этом более подробно сказано в разделе "Информация") от 30 до 25%'
    bot.send_message(message.chat.id, text)


bot.polling()

