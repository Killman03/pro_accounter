#!/bin/bash

# Скрипт автоматического деплоя бота на VPS
# Использование: ./deploy.sh

set -e  # Остановка при ошибке

echo "🚀 Начинаем деплой бота на VPS..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка, что скрипт запущен от root
if [[ $EUID -ne 0 ]]; then
   error "Этот скрипт должен быть запущен от имени root"
   exit 1
fi

# Обновление системы
log "Обновление системы..."
apt update && apt upgrade -y

# Установка необходимых пакетов
log "Установка Python и зависимостей..."
apt install -y python3 python3-pip python3-venv

log "Установка PostgreSQL..."
apt install -y postgresql postgresql-contrib

log "Установка дополнительных зависимостей..."
apt install -y build-essential python3-dev libpq-dev git

# Запуск и настройка PostgreSQL
log "Настройка PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# Создание директории для проекта
log "Создание директории проекта..."
mkdir -p /opt/coffee_bot
cd /opt/coffee_bot

# Проверка наличия файлов проекта
if [ ! -f "bot.py" ]; then
    error "Файл bot.py не найден в текущей директории"
    error "Убедитесь, что вы запускаете скрипт из корня проекта"
    exit 1
fi

# Создание виртуального окружения
log "Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
log "Установка Python зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt
pip install python-dotenv

# Проверка наличия файла .env
if [ ! -f ".env" ]; then
    warn "Файл .env не найден. Создайте его вручную с переменными окружения"
    cat > .env.example << EOF
BOT_TOKEN=your_telegram_bot_token_here
DB_HOST=localhost
DB_PORT=5432
DB_USER=coffee_user
DB_PASSWORD=your_secure_password
DB_NAME=coffee_rent
EOF
    log "Создан пример файла .env.example"
fi

# Создание systemd сервиса
log "Создание systemd сервиса..."
cat > /etc/systemd/system/coffee-bot.service << EOF
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
EOF

# Активация сервиса
log "Активация systemd сервиса..."
systemctl daemon-reload
systemctl enable coffee-bot

# Создание скрипта обновления
log "Создание скрипта обновления..."
cat > /opt/coffee_bot/update.sh << 'EOF'
#!/bin/bash
cd /opt/coffee_bot
echo "Обновление бота..."
if [ -d ".git" ]; then
    git pull
else
    echo "Git репозиторий не найден. Обновление пропущено."
fi
source venv/bin/activate
pip install -r requirements.txt
systemctl restart coffee-bot
echo "Бот обновлен и перезапущен!"
EOF

chmod +x /opt/coffee_bot/update.sh

# Настройка firewall
log "Настройка firewall..."
apt install -y ufw
ufw allow ssh
ufw --force enable

# Создание скрипта бэкапа
log "Создание скрипта резервного копирования..."
cat > /opt/coffee_bot/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/coffee_bot/backups"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
sudo -u postgres pg_dump coffee_rent > $BACKUP_DIR/backup_$DATE.sql
echo "Бэкап создан: backup_$DATE.sql"
# Удаление старых бэкапов (оставляем последние 7)
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
EOF

chmod +x /opt/coffee_bot/backup.sh

# Создание директории для бэкапов
mkdir -p /opt/coffee_bot/backups

# Настройка автоматического бэкапа
log "Настройка автоматического бэкапа..."
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/coffee_bot/backup.sh") | crontab -

# Установка прав доступа
log "Настройка прав доступа..."
chown -R root:root /opt/coffee_bot
chmod -R 755 /opt/coffee_bot

# Запуск сервиса
log "Запуск бота..."
systemctl start coffee-bot

# Проверка статуса
sleep 3
if systemctl is-active --quiet coffee-bot; then
    log "✅ Бот успешно запущен!"
else
    error "❌ Ошибка запуска бота"
    log "Проверьте логи: journalctl -u coffee-bot -n 50"
    exit 1
fi

# Вывод полезной информации
echo ""
echo "🎉 Деплой завершен успешно!"
echo ""
echo "📋 Полезные команды:"
echo "  Статус бота:     systemctl status coffee-bot"
echo "  Перезапуск:      systemctl restart coffee-bot"
echo "  Остановка:       systemctl stop coffee-bot"
echo "  Логи:            journalctl -u coffee-bot -f"
echo "  Обновление:      /opt/coffee_bot/update.sh"
echo "  Бэкап:           /opt/coffee_bot/backup.sh"
echo ""
echo "⚠️  Не забудьте:"
echo "  1. Создать файл .env с правильными переменными окружения"
echo "  2. Настроить базу данных PostgreSQL"
echo "  3. Протестировать бота в Telegram"
echo ""
echo "🔧 Для настройки базы данных выполните:"
echo "  sudo -u postgres psql"
echo "  CREATE DATABASE coffee_rent;"
echo "  CREATE USER your_user WITH PASSWORD 'your_password';"
echo "  GRANT ALL PRIVILEGES ON DATABASE coffee_rent TO your_user;"
echo "  \q" 