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
VALID_VALUES = ('rejected', 'approved',)

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    while True:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        if homework_name == None:
            logging.error(msg='Ошибка в получении имени ДЗ', exc_info=True)
        if homework_status == None:
            logging.error(msg='Ошибка в получении статуса ДЗ', exc_info=True)
        if homework_status not in VALID_VALUES:
            logging.error(msg='Статус может быть только <approved>\
                           или <rejected>', exc_info=True)
            time.sleep(5)
            continue
        if homework_status == 'rejected':
            verdict = 'К сожалению в работе нашлись ошибки.'
        else:
            verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp=None):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    while True:
        try:
            homework_statuses = requests.get(url, headers=headers, params=params)
            return homework_statuses.json()
        except (requests.RequestException, ValueError):
            logging.error(msg = 'index_err', exc_info=True)
            time.sleep(5)
            continue


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')  # обновить timestamp
            time.sleep(300)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()