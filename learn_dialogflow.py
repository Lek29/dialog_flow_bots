import json
import os

from environs import Env
from google.cloud import dialogflow_v2 as dialogflow


def create_intent(project_id, display_name, training_phrases_parts, message_texts, credentials_path):
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

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

    PARENT_PATH = dialogflow.AgentsClient.agent_path(project_id)

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

    response = intents_client.create_intent(
            request={'parent': PARENT_PATH, 'intent': intent}
        )
    return response


def main():
    """Основная точка входа для создания интентов Dialogflow из файла JSON.
    """

    env = Env()
    env.read_env()
    project_id = env.str('PROJECT_ID')
    credentials_file_name = env.str('GOOGLE_APPLICATION_CREDENTIALS')
    credentials_path = os.path.join(os.getcwd(), credentials_file_name)

    try:
        with open('questions.json', 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
    except FileNotFoundError:
        print('Ошибка: Файл "questions.json" не найден.')
        raise
    except json.JSONDecodeError:
        print('Ошибка: Файл "questions.json" содержит некорректный формат JSON.')
        raise

    print('Начинаем создание интентов в Dialogflow...')

    for intent_name, data in questions_data.items():
        try:
            print(f"\nСоздаем интент: '{intent_name}'")
            create_intent(
                project_id,
                intent_name,
                data['questions'],
                [data['answer']],
                credentials_path
            )
        except Exception as e:
            print(f'Ошибка при создании интента "{intent_name}": {e}')
    print('\nПроцесс создания интентов завершен.')


if __name__ == '__main__':
    main()
