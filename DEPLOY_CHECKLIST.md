# Чек-лист деплоя бота на VPS

## ✅ Подготовка
- [ ] Создан файл `.env` с переменными окружения
- [ ] Все файлы проекта готовы к загрузке
- [ ] Получены данные доступа к VPS (IP, логин, пароль)

## ✅ Подключение к серверу
- [ ] Подключение по SSH: `ssh root@your_server_ip`
- [ ] Обновление системы: `apt update && apt upgrade -y`

## ✅ Установка зависимостей
- [ ] Python3 и pip: `apt install python3 python3-pip python3-venv -y`
- [ ] PostgreSQL: `apt install postgresql postgresql-contrib -y`
- [ ] Дополнительные пакеты: `apt install build-essential python3-dev libpq-dev -y`

## ✅ Настройка базы данных
- [ ] Запуск PostgreSQL: `systemctl start postgresql && systemctl enable postgresql`
- [ ] Создание БД и пользователя:
  ```sql
  sudo -u postgres psql
  CREATE DATABASE coffee_rent;
  CREATE USER your_db_user WITH PASSWORD 'your_db_password';
  GRANT ALL PRIVILEGES ON DATABASE coffee_rent TO your_db_user;
  \q
  ```

## ✅ Загрузка проекта
- [ ] Создание директории: `mkdir -p /opt/coffee_bot && cd /opt/coffee_bot`
- [ ] Загрузка файлов (git/scp/sftp)
- [ ] Создание виртуального окружения: `python3 -m venv venv`
- [ ] Активация окружения: `source venv/bin/activate`
- [ ] Установка зависимостей: `pip install -r requirements.txt`
- [ ] Установка python-dotenv: `pip install python-dotenv`

## ✅ Настройка переменных окружения
- [ ] Создание файла `.env` с правильными значениями
- [ ] Проверка содержимого: `cat .env`

## ✅ Настройка systemd сервиса
- [ ] Создание файла `/etc/systemd/system/coffee-bot.service`
- [ ] Активация сервиса:
  ```bash
  systemctl daemon-reload
  systemctl enable coffee-bot
  systemctl start coffee-bot
  ```

## ✅ Настройка безопасности
- [ ] Установка UFW: `apt install ufw -y`
- [ ] Настройка firewall: `ufw allow ssh && ufw enable`
- [ ] Изменение пароля root: `passwd`

## ✅ Тестирование
- [ ] Проверка статуса сервиса: `systemctl status coffee-bot`
- [ ] Просмотр логов: `journalctl -u coffee-bot -f`
- [ ] Тестирование бота в Telegram (команда `/start`)

## ✅ Дополнительно
- [ ] Создание скрипта обновления: `/opt/coffee_bot/update.sh`
- [ ] Настройка автоматического бэкапа в crontab
- [ ] Настройка SSH ключей (опционально)

## 🔧 Команды для управления
```bash
# Перезапуск бота
systemctl restart coffee-bot

# Остановка бота
systemctl stop coffee-bot

# Просмотр логов
journalctl -u coffee-bot -f

# Проверка статуса
systemctl status coffee-bot
```

## 🚨 Решение проблем
```bash
# Если бот не запускается
journalctl -u coffee-bot -n 50

# Если проблемы с БД
systemctl status postgresql

# Если проблемы с зависимостями
cd /opt/coffee_bot
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
``` 