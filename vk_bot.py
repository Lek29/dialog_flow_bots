import logging
import random

import vk_api
from environs import Env
from vk_api.longpoll import VkEventType, VkLongPoll

from dialogflow_utils import detect_intent_texts
from telegram_notifier import send_dev_alert


logger = logging.getLogger(__name__)


def send_vk_message(vk_api_instance, user_id, message_text):
    try:
        vk_api_instance.messages.send(
            user_id=user_id,
            message=message_text,
            random_id=random.randint(1, 1000000)
        )
        logger.info(f'VK-бот: Отправлен ответ пользователю {user_id}: {message_text[:50]}...')
    except vk_api.exceptions.ApiError as e:
        logger.error(f'VK-бот: Ошибка VK API при отправке сообщения: {e}', exc_info=True)
        send_dev_alert(f'VK-бот: Ошибка VK API при отправке!\n\n```\n{e}\n```')
    except Exception as e:
        logger.error(f'VK-бот: Неожиданная ошибка при отправке сообщения: {e}', exc_info=True)
        send_dev_alert(f'VK-бот: Неожиданная ошибка при отправке!\n\n```\n{e}\n```')


def run_vk_bot():
    env = Env()
    env.read_env()

    VK_TOKEN = env.str('VK_TOKEN')

    if not VK_TOKEN:
        logger.error('Ошибка: VK_TOKEN не найден. Убедитесь, что он указан в .env файле.')
        send_dev_alert('VK-бот: VK_TOKEN не найден. Бот не запущен.')
        return

    logger.info('VK-бот: Токен загружен. Запуск бота...')

    try:
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk_api_instance = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)

        logger.info('VK-бот: Сессия и LongPoll инициализированы.')
        logger.info('VK-бот запущен и слушает события...')

        for event in longpoll.listen():
            if event.type != VkEventType.MESSAGE_NEW or not event.to_me:
                continue

            user_id = event.user_id
            user_text = event.text
            logger.info(f'VK-бот: Новое сообщение от {user_id}: "{user_text}"')


            dialogflow_response_text = 'Извините, я не понял ваш запрос. Пожалуйста, попробуйте еще раз.'

            try:
                query_result = detect_intent_texts(f'vk-{user_id}', user_text, 'ru')

                if not query_result:
                    logger.warning(f'VK-бот: Dialogflow не вернул результат для {user_id}: {user_text}')

                elif query_result.intent.is_fallback:
                    logger.info(f'VK-бот: Dialogflow fallback для {user_id}. Текст: {user_text}')
                else:
                    if query_result.fulfillment_text:
                        dialogflow_response_text = query_result.fulfillment_text
                        logger.info(
                            f'VK-бот: Отправлен ответ Dialogflow пользователю {user_id}: {dialogflow_response_text[:50]}...')
                    else:
                        logger.warning(
                            f"VK-бот: Dialogflow вернул интент без fulfillment_text для {user_id}. Запрос: {user_text}. Интент: {query_result.intent.display_name}")

            except Exception as e:
                logger.critical(f'VK-бот: Ошибка Dialogflow или обработки сообщения для {user_id}: {e}', exc_info=True)
                send_dev_alert(
                    f'VK-бот: Критическая ошибка Dialogflow!\n\nОт пользователя {user_id}: "{user_text}"\n\n```\n{e}\n```')
                dialogflow_response_text = 'Извините, произошла внутренняя ошибка при обработке вашего запроса.'


            send_vk_message(vk_api_instance, user_id, dialogflow_response_text)

    except Exception as e:
        logger.error(f"VK-бот: Критическая ошибка в цикле прослушивания событий: {e}", exc_info=True)
        send_dev_alert(f"VK-бот: Критическая ошибка в цикле прослушивания!\nОшибка: {e}")

    except vk_api.exceptions.ApiError as e:
        logger.critical(f'VK-бот: Критическая ошибка VK API (Long Poll): {e}', exc_info=True)
        send_dev_alert(f'VK-бот: Критическая ошибка VK API при инициализации/Long Poll!\n\n```\n{e}\n```')
    except Exception as e:
        logger.critical(f'VK-бот: Неожиданная ошибка при запуске VK-бота: {e}', exc_info=True)
        send_dev_alert(f'VK-бот: Неожиданная критическая ошибка при запуске!\n\n```\n{e}\n```')


if __name__ == '__main__':
    run_vk_bot()