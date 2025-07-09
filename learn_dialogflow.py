import json
import os

from environs import Env
from google.cloud import dialogflow_v2 as dialogflow

env = Env()
env.read_env()

PROJECT_ID = env.str('PROJECT_ID')

credentials_file_name = env.str('GOOGLE_APPLICATION_CREDENTIALS')
credentials_path = os.path.join(os.getcwd(), credentials_file_name)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

PARENT_PATH = dialogflow.AgentsClient.agent_path(PROJECT_ID)


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    """Создает новый интент (намерение) в Dialogflow.

        Этот интент будет содержать указанные тренировочные фразы и текстовые ответы.

        Args:
            project_id (str): ID проекта Google Cloud, где находится Dialogflow агент.
            display_name (str): Отображаемое имя интента в консоли Dialogflow.
            training_phrases_parts (list[str]): Список строк, которые будут
                использованы как тренировочные фразы для данного интента.
            message_texts (list[str]): Список строк, которые будут
                использованы как текстовые ответы (fulfillment messages) для данного интента.
                (В текущей реализации ожидается список из одной строки).

        Returns:
            None: Функция ничего не возвращает, но выводит информацию о создании
                или ошибке в консоль.
    """
    intents_client = dialogflow.IntentsClient()

    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)

        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part],
                                                           type_=dialogflow.Intent.TrainingPhrase.Type.EXAMPLE)
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message],
    )

    try:
        response = intents_client.create_intent(
            request={'parent': PARENT_PATH, 'intent': intent}
        )
        print(f'Интент "{response.display_name}" успешно создан. ID: {response.name}')
    except Exception as e:
        print(f'Ошибка при создании интента "{display_name}": {e}')


if __name__ == '__main__':
    """Основная точка входа для создания интентов Dialogflow из файла JSON.

       Загружает вопросы и ответы из 'questions.json' и использует их для
       создания или обновления интентов в указанном проекте Dialogflow.

       Ожидает наличие файла 'questions.json' в корневой директории
       и корректно настроенных переменных окружения (.env).
    """
    try:
        with open('questions.json', 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
    except FileNotFoundError:
        print('Ошибка: Файл "questions.json" не найден.')
        exit()
    except json.JSONDecodeError:
        print('Ошибка: Файл "questions.json" содержит некорректный формат JSON.')
        exit()

    print('Начинаем создание интентов в Dialogflow...')

    for intent_name, data in questions_data.items():
        print(f"\nСоздаем интент: '{intent_name}'")
        create_intent(
            PROJECT_ID,
            intent_name,
            data['questions'],
            [data['answer']]
        )

    print('\nПроцесс создания интентов завершен.')
