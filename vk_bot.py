import os
import random
import json
from environs import Env
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from google.cloud import dialogflow_v2 as dialogflow

env = Env()
env.read_env()

VK_TOKEN = env.str("VK_TOKEN")
PROJECT_ID = env.str("PROJECT_ID")

# vk_session = vk_api.VkApi(token=VK_TOKEN)
# longpoll = VkLongPoll(vk_session)
credentials_file_name = env.str("GOOGLE_APPLICATION_CREDENTIALS")
credentials_path = os.path.join(os.getcwd(), credentials_file_name)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
PARENT_PATH = dialogflow.AgentsClient.agent_path(PROJECT_ID)

def echo(event, vk_api_instance):
    vk_api_instance.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1, 1000000)
    )

def run_vk_bot():
    if not VK_TOKEN:
        print("Ошибка: VK_TOKEN не найден. Убедитесь, что он указан в .env файле.")
        return

    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk_api_instance = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    print("VK Эхо-бот запущен. Ожидаю сообщения...")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            print('Новое сообщение:')
            if event.to_me:
                print('Для меня от: ', event.user_id)
            else:
                print('От меня для: ', event.user_id)
            print('Текст:', event.text)

            # Вызываем функцию echo, чтобы бот ответил
            echo(event, vk_api_instance)

if __name__ == '__main__':
    run_vk_bot()