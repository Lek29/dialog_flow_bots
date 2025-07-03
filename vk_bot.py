import random
import json
from environs import Env
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dialogflow_utils import detect_intent_texts


env = Env()
env.read_env()

VK_TOKEN = env.str("VK_TOKEN")

def send_vk_message(vk_api_instance, user_id, message_text):
    vk_api_instance.messages.send(
        user_id=user_id,
        message=message_text,
        random_id=random.randint(1, 1000000)
    )

def run_vk_bot():
    if not VK_TOKEN:
        return

    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk_api_instance = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)


    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            user_text = event.text
            print(f'Новое сообщение от {user_id}: {user_text}')

            query_result = detect_intent_texts(str(user_id), user_text, "ru")

            if query_result:
                if query_result.intent.is_fallback:
                    pass
                else:
                    dialogflow_response_text = query_result.fulfillment_text
                    send_vk_message(vk_api_instance, user_id, dialogflow_response_text)
            else:
                pass


if __name__ == '__main__':
    run_vk_bot()