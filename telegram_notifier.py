import logging

from environs import Env
from telegram import Bot

logger = logging.getLogger(__name__)

env = Env()
env.read_env()

TELEGRAM_NOTIFIER_TOKEN = env.str('BOT_TOKEN')

DEVELOPER_CHAT_ID = env.str('DEVELOPER_CHAT_ID', None)

_notifier_bot = None


def _initialize_notifier_bot():
    global _notifier_bot

    if not TELEGRAM_NOTIFIER_TOKEN:
        logger.warning(
            'TELEGRAM_DEV_ALERT_BOT_TOKEN не установлен в .env. Уведомления об ошибках не будут отправляться.')
        return

    if not DEVELOPER_CHAT_ID:
        logger.warning('TELEGRAM_DEV_ALERT_CHAT_ID не установлен в .env. Уведомления об ошибках не будут отправляться.')
        return

    try:
        _notifier_bot = Bot(token=TELEGRAM_NOTIFIER_TOKEN)
        logger.info('Notifier Bot успешно инициализирован.')
    except Exception as e:
        logger.error(f'Ошибка при инициализации Notifier Bot: {e}')
        _notifier_bot = None

def send_dev_alert(message: str):
    if _notifier_bot and DEVELOPER_CHAT_ID:
        try:
            _notifier_bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message)
            logger.info(f'Отправлено уведомление в Telegram: {message[:100]}...')
        except Exception as e:
            logger.error(f'Не удалось отправить уведомление в Telegram чат {DEVELOPER_CHAT_ID}: {e}')
    else:
        logger.error(
            'Невозможно отправить уведомление: Notifier Bot не инициализирован или DEVELOPER_CHAT_ID не указан.')


_initialize_notifier_bot()