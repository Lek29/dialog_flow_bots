from telegram import Update
from telegram.ext import CallbackContext

import os
from environs import Env
from google.cloud import dialogflow_v2 as dialogflow


env = Env()
env.read_env()
PROJECT_ID = env.str("PROJECT_ID")

credentials_file_name = env.str("GOOGLE_APPLICATION_CREDENTIALS")
credentials_path = os.path.join(os.getcwd(), credentials_file_name)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

def detect_intent_texts(project_id, session_id, texts, language_code):

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)


    text = texts[0]
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    try:
        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        return response.query_result.fulfillment_text
    except Exception as e:

        print(f"Ошибка при обращении к Dialogflow API: {e}")
        return None



def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_html(
        f"Привет, {user.mention_html()}! Я теперь умный бот. Попробуй поздороваться!",
    )


def echo(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text
    telegram_user_id = str(update.message.from_user.id)

    dialogflow_response = detect_intent_texts(PROJECT_ID, telegram_user_id, [user_text], "ru")

    if dialogflow_response:
        update.message.reply_text(dialogflow_response)
    else:
        update.message.reply_text("Извините, я не смог понять ваш запрос. Пожалуйста, попробуйте еще раз.")
