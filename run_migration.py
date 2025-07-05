#!/usr/bin/env python3
"""
Скрипт для выполнения миграции: удаление поля payment_date из таблицы coffee_machines
"""

import asyncio
import asyncpg
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

async def run_migration():
    """Выполняет миграцию для удаления поля payment_date"""
    
    # Подключаемся к базе данных
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    
    try:
        print("🔍 Проверяем структуру таблицы coffee_machines...")
        
        # Проверяем, существует ли поле payment_date
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'coffee_machines' AND column_name = 'payment_date'
        """)
        
        if columns:
            print(f"📋 Найдено поле payment_date: {columns[0]}")
            print("🗑️  Удаляем поле payment_date...")
            
            # Удаляем поле
            await conn.execute("ALTER TABLE coffee_machines DROP COLUMN payment_date")
            print("✅ Поле payment_date успешно удалено!")
        else:
            print("ℹ️  Поле payment_date не найдено (уже удалено)")
        
        # Показываем новую структуру таблицы
        print("\n📊 Новая структура таблицы coffee_machines:")
        new_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'coffee_machines'
            ORDER BY ordinal_position
        """)
        
        for col in new_columns:
            print(f"  - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
            
    except Exception as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    print("🚀 Запуск миграции: удаление поля payment_date")
    print("=" * 50)
    
    asyncio.run(run_migration())
    
    print("\n" + "=" * 50)
    print("✅ Миграция завершена!")
    print("💡 Теперь можно запускать бота") 