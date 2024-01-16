import json
import logging
import os
import sys
import time
from http import HTTPStatus
from logging import StreamHandler

from dotenv import load_dotenv
import requests
import telegram

import exceptions

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяем доступность токенов."""
    if TELEGRAM_TOKEN and PRACTICUM_TOKEN and TELEGRAM_CHAT_ID:
        logger.debug('Переменные окружения присутствуют.')
        return True
    return False


def send_message(bot, message):
    """Отправляем сообщение в телеграм."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug('Сообщение отправлено')
    except Exception as error:
        logger.error('Не удалось отправить сообщение.')
        raise exceptions.TelegramError(
            f'Не удалась отправка сообщения. Неверный chat_id {error}',
        )


def get_api_answer(timestamp):
    """Делаем запрос к эндпойнту практикума."""
    url = ENDPOINT
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    payload = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
        if homework_statuses.status_code != HTTPStatus.OK:
            raise ConnectionError('Сервер не ответил.')
        return homework_statuses.json()
    except json.JSONDecodeError as error:
        raise exceptions.JsonError(f'Не в json. {error}')
    except requests.exceptions.RequestException as error:
        message = error.response.text
        raise exceptions.InvalidResponse(
            f'Не удалось сделать запрос к эндпойнту. {message}'
        )


def check_response(response):
    """Проверяем ответ сервера."""
    if type(response) is not dict:
        raise TypeError('Неверный тип данных в ответе сервера.')
    if 'homeworks' not in response or 'current_date' not in response:
        raise KeyError('В ответе сервера нет ключа домашки.')
    if type(response['homeworks']) is not list:
        raise TypeError('Данные не являются списком.')
    logger.debug('Ответ от сервера получен. check response.')
    return response['homeworks']


def parse_status(homework):
    """Вытягиваем статус работы из ответа сервера."""
    if 'homework_name' not in homework or 'status' not in homework:
        raise exceptions.EmptyResponse(
            'В ответе сервера нет ключа с названием домашки'
            'или ключа со статусом домашки.'
        )
    status = homework['status']
    if status in HOMEWORK_VERDICTS:
        verdict = HOMEWORK_VERDICTS[status]
        homework_name = homework['homework_name']
        logger.debug('Ответ от сервера получен верный.')
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    logger.error('Неверный ответ сервера.')
    raise exceptions.InvalidResponse('Неверный ответ сервера.')


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствуют переменные окружения')
        sys.exit('Отсутствуют данные окружения. Завершаю работу.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    status_prev = ''
    while True:
        try:
            response = get_api_answer(timestamp=timestamp)
            homeworks = check_response(response=response)
            timestamp = response['current_date']
            if len(homeworks) == 0:
                message = 'Видимо, работа пока не взята на проверку.'
                if status_prev != message:
                    send_message(message=message, bot=bot)
                logger.debug('Статус домашки не изменился.')
                status_prev = message
            else:
                homework = homeworks[0]
                status = homework['status']
                message = parse_status(homework=homework)
                if status != status_prev:
                    send_message(message=message, bot=bot)
                    status_prev = status
        except Exception as error:
            message = f'Сбой в работе программы. {error}'
            send_message(bot=bot, message=message)
            logger.error(message)
            raise exceptions.ProgrammError('Сбой в работе программы.')
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
