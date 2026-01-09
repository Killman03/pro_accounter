# pro_accounter — Telegram-бот для контроля аренды кофемашин

## Технологии
- Python, Aiogram 3.x, asyncpg (PostgreSQL)
- Pandas (Excel-отчеты)
- Plotly (графики)

## Запуск

### 🐳 Docker (Рекомендуется для VPS)

1. Скопируйте `env.example` в `.env` и заполните переменные:
   ```bash
   cp env.example .env
   nano .env  # или любой редактор
   ```

2. Запустите всё одной командой:
   ```bash
   docker compose up -d --build
   ```

3. Проверить логи:
   ```bash
   docker compose logs -f bot
   ```

4. Остановить:
   ```bash
   docker compose down
   ```

### Локальный запуск (без Docker)

1. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
2. Настройте переменные окружения или config.py (токен Telegram, параметры PostgreSQL).
3. Запустите бот:
   ```
   python bot.py
   ```

## Функционал
- Добавление кофемашин через инлайн-форму
- Автонапоминания о платежах
- Excel-отчеты и графики
- Сценарии аренды и выкупа

## 🚀 Быстрый деплой изменений

Для быстрого внесения изменений на сервер используйте один из методов:

### Вариант 1: Через Git (Рекомендуется) ⭐

```bash
# После внесения изменений:
git add .
git commit -m "Описание изменений"
git push

# Обновление на сервере:
ssh root@your_server_ip '/opt/coffee_bot/update.sh'
```

Или используйте скрипт `deploy.bat` (Windows) или создайте алиас для одной команды.

### Вариант 2: Через rsync

**Linux/Mac:**
```bash
./deploy_quick.sh root@your_server_ip
```

**Windows:**
```powershell
.\deploy_quick.ps1 -Server "root@your_server_ip"
```

📖 **Подробная инструкция:** см. [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

## 🐳 Docker-деплой на VPS

### Первоначальная настройка сервера

```bash
# Подключаемся к VPS
ssh root@your_server_ip

# Устанавливаем Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com | sh

# Клонируем репозиторий
git clone https://github.com/your_username/pro_accounter.git
cd pro_accounter

# Создаём .env файл
cp env.example .env
nano .env  # заполняем BOT_TOKEN, ADMIN_ID, DB_PASSWORD

# Запускаем
docker compose up -d --build
```

### Обновление на VPS

```bash
cd /path/to/pro_accounter
git pull
docker compose up -d --build
```

### Полезные команды

```bash
# Логи бота
docker compose logs -f bot

# Логи базы данных  
docker compose logs -f db

# Перезапуск
docker compose restart bot

# Остановить и удалить контейнеры (данные сохранятся)
docker compose down

# Полная очистка (УДАЛИТ ВСЕ ДАННЫЕ!)
docker compose down -v
```

### Бэкап базы данных

```bash
# Создать бэкап
docker compose exec db pg_dump -U postgres coffee_rent > backup_$(date +%Y%m%d).sql

# Восстановить из бэкапа
cat backup.sql | docker compose exec -T db psql -U postgres coffee_rent
```

## 📚 Документация

- [QUICK_DEPLOY.md](QUICK_DEPLOY.md) - Руководство по быстрому деплою
- [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) - Полное руководство по деплою на VPS
- [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md) - Чек-лист деплоя