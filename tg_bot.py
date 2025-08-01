import logging

from environs import Env
from telegram import Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

from dialogflow_utils import detect_intent_texts
from telegram_notifier import send_dev_alert

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_html(
        f'Привет, {user.mention_html()}! Я теперь умный бот. Попробуй поздороваться!',
    )
    logger.info(f'Telegram-бот: Пользователь {user.id} начал диалог.')


def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    user_text = update.message.text
    logger.info(f'Telegram-бот: Новое сообщение от {user_id}: "{user_text}"')

    try:
        query_result = detect_intent_texts(f'tg-{user_id}', user_text, 'ru')

        if query_result.intent.is_fallback:
            dialogflow_response_text = 'Извините, я не понял ваш запрос. Пожалуйста, попробуйте еще раз.'
            logger.info(f'Telegram-бот: Dialogflow fallback для {user_id}. Текст: {user_text}')
        else:
            dialogflow_response_text = query_result.fulfillment_text
            logger.info(
                f'Telegram-бот: Отправлен ответ Dialogflow пользователю {user_id}: {dialogflow_response_text[:50]}...')

        update.message.reply_text(dialogflow_response_text)

    except Exception as e:
        logger.critical(f'Telegram-бот: Ошибка Dialogflow или обработки сообщения для {user_id}: {e}', exc_info=True)
        send_dev_alert(
            f'Telegram-бот: Критическая ошибка Dialogflow!\n\nОт пользователя {user_id}: "{user_text}"\n\n```\n{e}\n```')
        update.message.reply_text('Произошла внутренняя ошибка. Пожалуйста, попробуйте позже.')


def error_handler(update: object, context: CallbackContext) -> None:
    logger.error(msg='Exception while handling an update:', exc_info=context.error)
    send_dev_alert(f'Telegram-бот: Необработанная ошибка в апдейте!\n\n```\n{context.error}\n```')


def run_tg_bot():
    env = Env()
    env.read_env()

    telegram_token = env.str('BOT_TOKEN')

    if not telegram_token:
        logger.error('telegram_token не установлен в .env. Telegram-бот не будет работать.')

        send_dev_alert('Telegram-бот: telegram_token не установлен в .env. Бот не запущен.')
        return

    logger.info('Telegram-бот: Запуск...')
    updater = Updater(telegram_token, use_context=True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    logger.info('Telegram-бот запущен и получает обновления.')


if __name__ == '__main__':
    run_tg_bot()
