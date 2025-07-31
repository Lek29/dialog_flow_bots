import logging

from environs import Env
from telegram import Bot

logger = logging.getLogger(__name__)

_get_notifier_resources = None

def _initialize_once():
    """
        Выполняет всю инициализацию и возвращает кортеж (бот, chat_id).
    """

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
    global _get_notifier_resources

    if _get_notifier_resources is None:
        bot, chat_id = _initialize_once()

        def _get_resources():
            return bot, chat_id

        _get_notifier_resources = _get_resources

    notifier_bot, developer_chat_id = _get_notifier_resources()

    if notifier_bot and developer_chat_id:
        try:
            notifier_bot.send_message(chat_id=developer_chat_id, text=message)
            logger.info(f'Отправлено уведомление в Telegram: {message[:100]}...')
        except Exception as e:
            logger.error(f'Не удалось отправить уведомление: {e}')
    else:
        logger.error(
            'Невозможно отправить уведомление: бот не инициализирован.')


if __name__ == '__main__':
    send_dev_alert("Тестовое уведомление")
