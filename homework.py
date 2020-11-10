import os
import requests
import telegram
import time
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
VALID_VALUES = ('rejected', 'approved')


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None:
        return 'Ошибка в получении имени ДЗ'
    if homework_status is None:
        return 'Ошибка в получении статуса ДЗ'
    if homework_status not in VALID_VALUES:
        return'Статус может быть только <approved> или <rejected>'
    if homework_status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    current_timestamp = current_timestamp or int(time.time())
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=params)
        return homework_statuses.json()
    except Exception as e:
        return f'Ошибка при попытке запроса к серверу: {e}'

# Яндекс поменял тесты: теперь нужно,
# чтобы функция принимала два аргумента
# + сответственно изменил вызов send_message в 61 строке
def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    # инициализировать бота согласно новому прекоду нужно здесь,
    # что я и сделал...
    telebot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]), telebot)
            current_timestamp = new_homework.get('current_date')
            time.sleep(300)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()