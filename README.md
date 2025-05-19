# Бот tgyandbot
Просто бот, который умеет показывать текущий трек из Я.Музыки 

## Зависимости
- uv (https://github.com/astral-sh/uv)
- *ИЛИ* python3.12 

## Установка
```bash
cp .env.example .env
```

В файле .env установите переменные: 
- API_URL - url для обращения к текущему серверу (требуется для создания приложения в https://oauth.yandex.ru, SSL - обязателен)
- YA_TOKEN - токен яндекс.музыки для скачивания треков - https://yandex-music.readthedocs.io/en/main/token.html
- YA_CLIENT_ID - id приложения для аутентификации - https://oauth.yandex.ru/
- TG_TOKEN - токен телеграм бота

```bash
uv venv
uv sync

# или без uv
pip install -r requirements.txt
```

## Запуск
```bash
uv run main.py

# или без uv 
python main.py
```