# Руководство по деплою бота на VPS сервер cp.jino.ru

## Подготовка к деплою

### 1. Подготовка файлов проекта

Перед деплоем убедитесь, что у вас есть:
- Все файлы проекта (bot.py, config.py, db.py, handlers/, utils/, etc.)
- Файл requirements.txt с зависимостями
- Файл .env с переменными окружения (НЕ загружайте в git!)

### 2. Создание файла .env

Создайте файл `.env` в корне проекта:
```env
BOT_TOKEN=your_telegram_bot_token_here
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=coffee_rent
```

## Этап 1: Подключение к VPS серверу

### 1.1 Получение доступа к серверу
1. Войдите в панель управления cp.jino.ru
2. Найдите данные для подключения к вашему VPS:
   - IP адрес сервера
   - Логин (обычно root)
   - Пароль или SSH ключ

### 1.2 Подключение по SSH
```bash
ssh root@your_server_ip
```

## Этап 2: Настройка сервера

### 2.1 Обновление системы
```bash
apt update && apt upgrade -y
```

### 2.2 Установка Python и pip
```bash
apt install python3 python3-pip python3-venv -y
```

### 2.3 Установка PostgreSQL
```bash
apt install postgresql postgresql-contrib -y
systemctl start postgresql
systemctl enable postgresql
```

### 2.4 Настройка PostgreSQL
```bash
# Переключение на пользователя postgres
sudo -u postgres psql

# Создание базы данных и пользователя
CREATE DATABASE coffee_rent;
CREATE USER your_db_user WITH PASSWORD 'your_db_password';
GRANT ALL PRIVILEGES ON DATABASE coffee_rent TO your_db_user;
\q
```

### 2.5 Установка дополнительных зависимостей
```bash
apt install build-essential python3-dev libpq-dev -y
```

## Этап 3: Загрузка проекта

### 3.1 Создание директории для проекта
```bash
mkdir -p /opt/coffee_bot
cd /opt/coffee_bot
```

### 3.2 Загрузка файлов проекта
Есть несколько способов:

#### Способ 1: Через Git (рекомендуется)
```bash
# Установка git
apt install git -y

# Клонирование репозитория
git clone https://github.com/your_username/pro_accounter.git .
```

#### Способ 2: Через SCP
```bash
# На локальной машине
scp -r /path/to/your/project/* root@your_server_ip:/opt/coffee_bot/
```

#### Способ 3: Через SFTP клиент
Используйте FileZilla или другой SFTP клиент для загрузки файлов.

### 3.3 Создание виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.4 Установка зависимостей
```bash
pip install -r requirements.txt
```

## Этап 4: Настройка переменных окружения

### 4.1 Создание файла .env
```bash
nano .env
```

Добавьте содержимое:
```env
BOT_TOKEN=your_actual_bot_token
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=coffee_rent
```

### 4.2 Установка python-dotenv
```bash
pip install python-dotenv
```

## Этап 5: Настройка systemd сервиса

### 5.1 Создание файла сервиса
```bash
nano /etc/systemd/system/coffee-bot.service
```

Добавьте содержимое:
```ini
[Unit]
Description=Coffee Bot Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/coffee_bot
Environment=PATH=/opt/coffee_bot/venv/bin
ExecStart=/opt/coffee_bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.2 Активация сервиса
```bash
systemctl daemon-reload
systemctl enable coffee-bot
systemctl start coffee-bot
```

## Этап 6: Настройка firewall

### 6.1 Установка и настройка UFW
```bash
apt install ufw -y
ufw allow ssh
ufw allow 5432/tcp  # PostgreSQL (если нужен внешний доступ)
ufw enable
```

## Этап 7: Тестирование и мониторинг

### 7.1 Проверка статуса сервиса
```bash
systemctl status coffee-bot
```

### 7.2 Просмотр логов
```bash
journalctl -u coffee-bot -f
```

### 7.3 Тестирование бота
1. Найдите вашего бота в Telegram
2. Отправьте команду `/start`
3. Проверьте все функции

## Этап 8: Настройка автоматических обновлений

### 8.1 Создание скрипта обновления
```bash
nano /opt/coffee_bot/update.sh
```

Добавьте содержимое:
```bash
#!/bin/bash
cd /opt/coffee_bot
git pull
source venv/bin/activate
pip install -r requirements.txt
systemctl restart coffee-bot
```

### 8.2 Делаем скрипт исполняемым
```bash
chmod +x /opt/coffee_bot/update.sh
```

## Полезные команды для управления

### Перезапуск бота
```bash
systemctl restart coffee-bot
```

### Остановка бота
```bash
systemctl stop coffee-bot
```

### Просмотр логов в реальном времени
```bash
journalctl -u coffee-bot -f
```

### Проверка использования ресурсов
```bash
htop
df -h
free -h
```

## Решение проблем

### 1. Бот не запускается
```bash
# Проверьте логи
journalctl -u coffee-bot -n 50

# Проверьте права доступа
ls -la /opt/coffee_bot/

# Проверьте переменные окружения
cat /opt/coffee_bot/.env
```

### 2. Проблемы с базой данных
```bash
# Проверьте статус PostgreSQL
systemctl status postgresql

# Подключитесь к базе данных
sudo -u postgres psql -d coffee_rent
```

### 3. Проблемы с зависимостями
```bash
# Переустановите виртуальное окружение
cd /opt/coffee_bot
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Резервное копирование

### Создание бэкапа базы данных
```bash
# Создание бэкапа
sudo -u postgres pg_dump coffee_rent > /opt/coffee_bot/backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из бэкапа
sudo -u postgres psql coffee_rent < /opt/coffee_bot/backup_file.sql
```

### Автоматическое резервное копирование
Добавьте в crontab:
```bash
crontab -e
# Добавьте строку для ежедневного бэкапа в 2:00
0 2 * * * sudo -u postgres pg_dump coffee_rent > /opt/coffee_bot/backup_$(date +\%Y\%m\%d).sql
```

## Безопасность

### 1. Изменение пароля root
```bash
passwd
```

### 2. Настройка SSH ключей
```bash
# На локальной машине
ssh-keygen -t rsa -b 4096
ssh-copy-id root@your_server_ip
```

### 3. Отключение парольной аутентификации SSH
```bash
nano /etc/ssh/sshd_config
# Установите PasswordAuthentication no
systemctl restart sshd
```

## Заключение

После выполнения всех этапов ваш бот должен работать стабильно на VPS сервере. Не забывайте:

1. Регулярно обновлять систему
2. Мониторить логи бота
3. Делать резервные копии базы данных
4. Следить за использованием ресурсов

При возникновении проблем всегда начинайте с проверки логов сервиса. 