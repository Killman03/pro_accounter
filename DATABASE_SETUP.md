# Настройка базы данных PostgreSQL

## Подключение к PostgreSQL

### 1. Переключение на пользователя postgres
```bash
sudo -u postgres psql
```

### 2. Создание базы данных
```sql
CREATE DATABASE coffee_rent;
```

### 3. Создание пользователя
```sql
CREATE USER coffee_user WITH PASSWORD 'your_secure_password';
```

### 4. Предоставление прав
```sql
GRANT ALL PRIVILEGES ON DATABASE coffee_rent TO coffee_user;
```

### 5. Выход из psql
```sql
\q
```

## Настройка подключения

### 1. Редактирование pg_hba.conf
```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

Добавьте или измените строки:
```
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
```

### 2. Перезапуск PostgreSQL
```bash
sudo systemctl restart postgresql
```

## Проверка подключения

### 1. Тест подключения
```bash
psql -h localhost -U coffee_user -d coffee_rent
```

### 2. Проверка таблиц (после первого запуска бота)
```sql
\dt
```

## Резервное копирование

### 1. Создание бэкапа
```bash
sudo -u postgres pg_dump coffee_rent > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Восстановление из бэкапа
```bash
sudo -u postgres psql coffee_rent < backup_file.sql
```

## Автоматическое резервное копирование

### 1. Создание скрипта бэкапа
```bash
nano /opt/coffee_bot/backup_db.sh
```

Содержимое скрипта:
```bash
#!/bin/bash
BACKUP_DIR="/opt/coffee_bot/backups"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
sudo -u postgres pg_dump coffee_rent > $BACKUP_DIR/db_backup_$DATE.sql
echo "Бэкап БД создан: db_backup_$DATE.sql"
# Удаление старых бэкапов (оставляем последние 30)
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +30 -delete
```

### 2. Делаем скрипт исполняемым
```bash
chmod +x /opt/coffee_bot/backup_db.sh
```

### 3. Добавление в crontab
```bash
crontab -e
```

Добавьте строку для ежедневного бэкапа в 3:00:
```
0 3 * * * /opt/coffee_bot/backup_db.sh
```

## Мониторинг базы данных

### 1. Проверка размера базы данных
```sql
SELECT pg_size_pretty(pg_database_size('coffee_rent'));
```

### 2. Проверка активных подключений
```sql
SELECT * FROM pg_stat_activity WHERE datname = 'coffee_rent';
```

### 3. Проверка производительности
```sql
SELECT schemaname, tablename, attname, n_distinct, correlation 
FROM pg_stats 
WHERE schemaname = 'public' 
ORDER BY n_distinct DESC;
```

## Решение проблем

### 1. Ошибка подключения
```bash
# Проверьте статус PostgreSQL
sudo systemctl status postgresql

# Проверьте логи
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### 2. Проблемы с правами доступа
```sql
-- Подключитесь как postgres
sudo -u postgres psql

-- Проверьте пользователей
\du

-- Пересоздайте пользователя если нужно
DROP USER IF EXISTS coffee_user;
CREATE USER coffee_user WITH PASSWORD 'new_password';
GRANT ALL PRIVILEGES ON DATABASE coffee_rent TO coffee_user;
```

### 3. Проблемы с памятью
Отредактируйте `/etc/postgresql/*/main/postgresql.conf`:
```
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

Перезапустите PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## Безопасность

### 1. Изменение пароля postgres
```bash
sudo -u postgres psql
\password
```

### 2. Ограничение доступа
В `/etc/postgresql/*/main/pg_hba.conf`:
```
# Разрешить подключения только с localhost
host    coffee_rent      coffee_user      127.0.0.1/32            md5
host    coffee_rent      coffee_user      ::1/128                 md5
```

### 3. Регулярное обновление паролей
Создайте скрипт для смены паролей:
```bash
nano /opt/coffee_bot/change_db_password.sh
```

```bash
#!/bin/bash
NEW_PASSWORD=$(openssl rand -base64 32)
sudo -u postgres psql -c "ALTER USER coffee_user WITH PASSWORD '$NEW_PASSWORD';"
echo "Новый пароль: $NEW_PASSWORD"
# Обновите .env файл
sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$NEW_PASSWORD/" /opt/coffee_bot/.env
echo "Пароль обновлен в .env файле"
``` 