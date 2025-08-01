import logging

from environs import Env
from telegram import Bot

logger = logging.getLogger(__name__)


def get_notifier_bot_and_chat_id():

    env = Env()
    env.read_env()

    token = env.str('BOT_TOKEN')
    chat_id = env.str('DEVELOPER_CHAT_ID', None)

    if not token:
        logger.warning(
            'TELEGRAM_DEV_ALERT_BOT_TOKEN не установлен в .env. Уведомления об ошибках не будут отправляться.')
        return None, None

    if not chat_id:
        logger.warning('TELEGRAM_DEV_ALERT_CHAT_ID не установлен в .env. Уведомления об ошибках не будут отправляться.')
        return None, None

    try:
        bot = Bot(token=token)
        logger.info('Notifier Bot успешно инициализирован.')
        return bot, chat_id
    except Exception as e:
        logger.error(f'Ошибка при инициализации Notifier Bot: {e}')
        return None, None


def send_dev_alert(message: str):

    bot, chat_id = get_notifier_bot_and_chat_id()

    if bot and chat_id:
        try:
            bot.send_message(chat_id=chat_id, text=message)
            logger.info(f'Отправлено уведомление в Telegram: {message[:100]}...')
        except Exception as e:
            logger.error(f'Не удалось отправить уведомление: {e}')
    else:
        logger.error(
            'Невозможно отправить уведомление: бот не инициализирован.')


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    send_dev_alert("Тестовое уведомление")
