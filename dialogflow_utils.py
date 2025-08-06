import os

from environs import Env
from google.cloud import dialogflow_v2 as dialogflow


def detect_intent_texts(project_id, credentials_path, session_id, text, language_code='ru-RU'):
    """
    Отправляет текстовый запрос в Dialogflow и возвращает ответ.

    """

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={'session': session, 'query_input': query_input}
    )
    return response.query_result


if __name__ == '__main__':
    env = Env()
    env.read_env()
    project_id = env.str('PROJECT_ID')
    credentials_file_name = env.str('GOOGLE_APPLICATION_CREDENTIALS')
    credentials_path = os.path.join(os.getcwd(), credentials_file_name)

    detect_intent_texts(project_id, credentials_path, 'test_session', 'Привет')
