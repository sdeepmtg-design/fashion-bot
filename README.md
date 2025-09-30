# Fashion Bot для Telegram (Docker)

Бот для публикации статей о моде из известных журналов.

## Функции:
- Получение свежих статей из Vogue, Harper's Bazaar, Elle, GQ
- Команда /latest - получить 2 свежие статьи
- Автоматическая работа 24/7 в Docker

## Как запустить на Render с Docker:

1. Создайте репозиторий на GitHub с этими файлами
2. Зайдите на render.com
3. Нажмите "New +" → "Web Service"
4. Подключите ваш GitHub репозиторий
5. В настройках:
   - **Environment**: Docker
   - **Dockerfile Path**: `Dockerfile` (оставьте по умолчанию)
6. Добавьте Environment Variable:
   - Key: TELEGRAM_BOT_TOKEN
   - Value: ваш_токен_от_BotFather
7. Нажмите "Create Web Service"

Готово! Бот будет работать в Docker контейнере.
