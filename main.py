import telebot
from telebot import types

bot = telebot.TeleBot('912680602:AAFuJ7VF3CuxO2_giada4gqGP_dwfLqkp5c')


def create_markup(keyboard, mod=0):
    if mod == 0:
        markup = types.ReplyKeyboardMarkup()
        for row in keyboard:
            cells = []
            for cell in row:
                item_btn = types.KeyboardButton(cell)
                cells.append(item_btn)
            markup.row(*cells)
        return markup
    else:
        markup = types.InlineKeyboardMarkup()
        for cell in keyboard:
            if type(cell) is str or len(cell) == 1:
                return None
            btn = types.InlineKeyboardButton(text=cell[0], url=cell[1])
            markup.add(btn)
        return markup


@bot.message_handler(commands=['start', 'help'])
def send_help(message):
    if message.text == '/help':
        bot.send_message(message.chat.id,
                         'По всем вопросам обращаться к @r6tuti, даже по самым тупым))')
    elif message.text == '/start':
        markup = create_markup(
            [['Расценки', 'Правила', 'Информация'], ['/help', '/start']])
        bot.send_message(message.chat.id, 'Какой-то вступительный текст',
                         reply_markup=markup)

        markup = create_markup(
            [['Отзывы', 'https://t.me/joinchat/R9n7l7rBOx1jZjIy'],
             ['Магазины', 'https://t.me/joinchat/R9n7l7rBOx1jZjIy']], 1)
        bot.send_message(message.chat.id,
                         'Ещё какой-то текст, чтоб объяснить ссылки ниже',
                         reply_markup=markup)


@bot.message_handler(content_types=['text'])
def echo_all(message):
    text = 'Сори я не понимаю тебя, пльзуйся кнопками'
    if message.text == 'Информация':
        text = 'Информация'
    elif message.text == 'Правила':
        text = 'В отличие от других шопов, я НЕСУ ответственность за неудачный реф или вбив, будет перезаказ!!!'
    elif message.text == 'Расценки':
        text = 'Цена не высока и варируется от кол-ва вашего заказа (об этом более подробно сказано в разделе "Информация") от 30 до 25%'
    bot.send_message(message.chat.id, text)


bot.polling()
