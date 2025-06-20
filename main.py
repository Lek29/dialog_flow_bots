from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from environs import Env

from handlers import start, echo


env = Env()
env.read_env()

bot_token = env.str('BOT_TOKEN')


def main():
    if not bot_token:
        print("Ошибка: BOT_TOKEN не найден. Убедитесь, что он указан в .env файле или как системная переменная.")
        return

    updater = Updater(bot_token, use_context=True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    print("Бот запущен! Отправьте ему /start или любое сообщение.")
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()