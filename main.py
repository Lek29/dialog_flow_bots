import threading
import sys
import traceback
import logging

from tg_bot import run_tg_bot
from vk_bot import run_vk_bot

from telegram_notifier import send_dev_alert

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def handle_exception(exc_type, exc_value, exc_traceback):
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    alert_msg = f"**ОШИБКА БОТА!** \n\n```python\n{error_msg}\n```"

    logger.critical(f"Критическая ошибка: {error_msg}")
    send_dev_alert(alert_msg)

    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = handle_exception

if __name__ == '__main__':
    logger.info("Запуск ботов...")
    threading.Thread(target=run_tg_bot(), daemon=True).start()
    threading.Thread(target=run_vk_bot, daemon=True).start()
    logger.info("Оба бота запущены в отдельных потоках.")

    threading.main_thread().join()