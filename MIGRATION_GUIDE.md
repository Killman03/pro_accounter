# Руководство по миграции базы данных

## Выполнение миграции на VPS

### 1. Подготовка к миграции

#### 1.1 Создание резервной копии
```bash
# Создайте бэкап перед миграцией
sudo -u postgres pg_dump coffee_rent > backup_before_migration_$(date +%Y%m%d_%H%M%S).sql
```

#### 1.2 Остановка бота
```bash
systemctl stop coffee-bot
```

### 2. Выполнение миграции

#### 2.1 Подключение к базе данных
```bash
sudo -u postgres psql coffee_rent
```

#### 2.2 Выполнение SQL-миграции
```sql
-- Удаляем колонку payment_date из таблицы coffee_machines
ALTER TABLE coffee_machines DROP COLUMN IF EXISTS payment_date;
```

#### 2.3 Проверка результата
```sql
-- Проверяем структуру таблицы
\d coffee_machines

-- Проверяем, что колонка удалена
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'coffee_machines' AND column_name = 'payment_date';
```

#### 2.4 Выход из psql
```sql
\q
```

### 3. Запуск бота с новой версией

#### 3.1 Обновление кода (если нужно)
```bash
cd /opt/coffee_bot
git pull  # если используете git
```

#### 3.2 Перезапуск бота
```bash
systemctl start coffee-bot
```

#### 3.3 Проверка статуса
```bash
systemctl status coffee-bot
```

### 4. Тестирование после миграции

#### 4.1 Проверка основных функций
1. Отправьте `/start` боту
2. Добавьте новую машину
3. Внесите платеж
4. Проверьте отчеты

#### 4.2 Проверка напоминаний
```bash
# Просмотр логов для проверки напоминаний
journalctl -u coffee-bot -f
```

### 5. Откат миграции (если потребуется)

#### 5.1 Восстановление из бэкапа
```bash
# Остановите бота
systemctl stop coffee-bot

# Восстановите базу данных
sudo -u postgres psql coffee_rent < backup_before_migration_YYYYMMDD_HHMMSS.sql

# Запустите бота
systemctl start coffee-bot
```

#### 5.2 Ручное восстановление колонки
```sql
-- Если нужно восстановить колонку вручную
ALTER TABLE coffee_machines ADD COLUMN payment_date DATE;
```

## Автоматизированная миграция

### Создание скрипта миграции
```bash
nano /opt/coffee_bot/migrate.sh
```

Содержимое скрипта:
```bash
#!/bin/bash

echo "🚀 Начинаем миграцию базы данных..."

# Создание бэкапа
BACKUP_FILE="backup_before_migration_$(date +%Y%m%d_%H%M%S).sql"
echo "📦 Создание бэкапа: $BACKUP_FILE"
sudo -u postgres pg_dump coffee_rent > /opt/coffee_bot/backups/$BACKUP_FILE

# Остановка бота
echo "⏹ Остановка бота..."
systemctl stop coffee-bot

# Выполнение миграции
echo "🔧 Выполнение миграции..."
sudo -u postgres psql coffee_rent -c "ALTER TABLE coffee_machines DROP COLUMN IF EXISTS payment_date;"

# Запуск бота
echo "▶️ Запуск бота..."
systemctl start coffee-bot

# Проверка статуса
sleep 3
if systemctl is-active --quiet coffee-bot; then
    echo "✅ Миграция завершена успешно!"
    echo "📋 Бэкап сохранен: /opt/coffee_bot/backups/$BACKUP_FILE"
else
    echo "❌ Ошибка запуска бота после миграции"
    echo "🔍 Проверьте логи: journalctl -u coffee-bot -n 50"
    exit 1
fi
```

### Делаем скрипт исполняемым
```bash
chmod +x /opt/coffee_bot/migrate.sh
```

### Запуск миграции
```bash
/opt/coffee_bot/migrate.sh
```

## Проверка целостности данных

### 1. Проверка количества записей
```sql
-- Проверяем количество машин
SELECT COUNT(*) FROM coffee_machines;

-- Проверяем количество платежей
SELECT COUNT(*) FROM payments;

-- Проверяем количество моделей
SELECT COUNT(*) FROM machine_models;
```

### 2. Проверка связей между таблицами
```sql
-- Проверяем, что все платежи связаны с машинами
SELECT COUNT(*) FROM payments p 
LEFT JOIN coffee_machines c ON p.machine_id = c.id 
WHERE c.id IS NULL;

-- Проверяем, что все машины имеют модели
SELECT COUNT(*) FROM coffee_machines c 
LEFT JOIN machine_models m ON c.model_id = m.id 
WHERE m.id IS NULL;
```

### 3. Проверка данных о платежах
```sql
-- Проверяем последние платежи
SELECT c.client_name, p.payment_date, p.amount 
FROM payments p 
JOIN coffee_machines c ON p.machine_id = c.id 
ORDER BY p.payment_date DESC 
LIMIT 10;
```

## Мониторинг после миграции

### 1. Настройка мониторинга логов
```bash
# Создание скрипта для мониторинга ошибок
nano /opt/coffee_bot/monitor_errors.sh
```

```bash
#!/bin/bash
# Мониторинг ошибок в логах бота
journalctl -u coffee-bot --since "1 hour ago" | grep -i error
```

### 2. Проверка производительности
```sql
-- Проверка размера таблиц
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Полезные команды для диагностики

### Проверка статуса сервисов
```bash
# Статус бота
systemctl status coffee-bot

# Статус PostgreSQL
systemctl status postgresql

# Проверка портов
netstat -tlnp | grep :5432
```

### Просмотр логов
```bash
# Логи бота
journalctl -u coffee-bot -f

# Логи PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Проверка подключений к БД
```sql
-- Активные подключения
SELECT * FROM pg_stat_activity WHERE datname = 'coffee_rent';

-- Статистика запросов
SELECT * FROM pg_stat_user_tables;
``` 