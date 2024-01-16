# python telegram bot

Telegram bot для проверки статуса домашней работы на ЯндексПрактикуме.

## Возможности бота:
- Раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы.
- При обновлении статуса анализирует ответ API и отправляет вам соответствующее уведомление в Telegram.
- Логгирует свою работу и сообщает вам о важных проблемах сообщением в Telegram.

## Запуск проекта:
Склонируйте репозиторий:
```bash
git clone https://github.com/shurikman82/API_Practicum_homework_bot.git
```
Создайте и ативируйте виртуальное окружение:
```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```
Установите зависимости:
```bash
pip install -r requirements.txt
```
Создайте файл `.env` на примере `.env.example`
Запустите файл `homework.py`:
```bash
python3 homework.py
```

## Автор:
Александр Русанов, shurik.82rusanov@yandex.ru.
