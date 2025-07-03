import os
from environs import Env
from google.cloud import dialogflow_v2 as dialogflow

env = Env()
env.read_env()

PROJECT_ID = env.str("PROJECT_ID")
credentials_file_name = env.str("GOOGLE_APPLICATION_CREDENTIALS")
credentials_path = os.path.join(os.getcwd(), credentials_file_name)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

PARENT_PATH = dialogflow.AgentsClient.agent_path(PROJECT_ID)

def detect_intent_texts(session_id, text, language_code='ru-RU'):
    """
    Отправляет текстовый запрос в Dialogflow и возвращает ответ.
    Использование одного и того же session_id позволяет продолжать диалог (контекст).

    Args:
        session_id (str): Уникальный идентификатор сессии для диалога. Обычно это ID пользователя.
        text (str): Текст сообщения пользователя.
        language_code (str): Код языка (например, 'ru-RU' для русского).

    Returns:
        str: Ответ из Dialogflow (fulfillment_text) или None, если произошла ошибка.
    """

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(PROJECT_ID, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    try:
        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        return response.query_result
    except Exception as e:
        return None