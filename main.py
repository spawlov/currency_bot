import telebot
from config import TOKEN, HELP
from excepions import BotUserException
from extentions import APICurses, Calculate

if __name__ == '__main__':

    bot = telebot.TeleBot(TOKEN)
    api = APICurses()

    @bot.message_handler(commands=['start', 'help'])
    def reply_help(message: telebot.types.Message):
        bot.send_message(message.chat.id, HELP)

    @bot.message_handler(commands=api.cur_list)
    def reply_curs(message: telebot.types.Message):
        # Возвращаем курс отдельно выбранной валюты
        bot.send_message(message.chat.id, api.currency(message.text))

    @bot.message_handler(commands=['values'])
    def reply_all(message: telebot.types.Message):
        # Возвращаем полный список валют с "кликабельными" командами
        bot.send_message(message.chat.id, api.all_currency)

    @bot.message_handler(content_types=['text'])
    def reply_convert(message: telebot.types.Message):
        # Конвертируем валюты
        try:
            base, sym, amount = message.text.split()
        except ValueError:
            BotUserException(
                bot.reply_to(
                    message, 'Неверно задано число параметров\n'
                             'или неверная команда'
                )
            )
        else:
            bot.reply_to(
                message, Calculate.convert(api.cbr_req, base, sym, amount)
            )


    bot.polling(none_stop=True)
