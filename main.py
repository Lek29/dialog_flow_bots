import logging
import sys
import threading
import traceback

from telegram_notifier import send_dev_alert
from tg_bot import run_tg_bot
from vk_bot import run_vk_bot


# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )
logger = logging.getLogger(__name__)


def handle_exception(exc_type, exc_value, exc_traceback):
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    alert_msg = f'**ОШИБКА БОТА!** \n\n```python\n{error_msg}\n```'

    logger.critical(f'Критическая ошибка: {error_msg}')
    send_dev_alert(alert_msg)

    sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_exception


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    sys.excepthook = handle_exception

    logger.info('Запуск ботов...')
    telegram_thread = threading.Thread(target=run_tg_bot, daemon=True)
    vk_thread = threading.Thread(target=run_vk_bot, daemon=True)

    telegram_thread.start()
    vk_thread.start()
    logger.info('Оба бота запущены в отдельных потоках.')


    try:
        telegram_thread.join()
        vk_thread.join()
    except KeyboardInterrupt:
        logger.info('Главный поток остановлен вручную. Завершение работы ботов.')
    except Exception as e:
        logger.critical(f'Неожиданная ошибка в главном потоке: {e}', exc_info=True)
        send_dev_alert(f'Неожиданная ошибка в главном потоке: {e}')


if __name__ == '__main__':
    main()
