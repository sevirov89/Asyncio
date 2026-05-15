import asyncpg
import asyncio
from config import DB_CONFIG


async def check_data():
    # Устанавливаем соединение для проверки загруженных данных
    conn = await asyncpg.connect(**DB_CONFIG)
    try:
        # Проверка количества записей
        count = await conn.fetchval('SELECT COUNT(*) FROM star_wars_people')
        print(f"Всего записей в базе: {count}")

        # Проверка нескольких случайных записей
        records = await conn.fetch('''
            SELECT id, name, gender, mass
            FROM star_wars_people
            ORDER BY RANDOM()
            LIMIT 5
        ''')

        print("\nПримеры записей:")
        for record in records:
            print(f"ID: {record['id']}, Name: {record['name']}, Gender: {record['gender']}, Mass: {record['mass']}")

        # Проверка конкретного персонажа
        luke = await conn.fetchrow('''
            SELECT * FROM star_wars_people
            WHERE name = 'Luke Skywalker'
        ''')

        if luke:
            print("\nДанные Люка Скайуокера:")
            print(dict(luke))
        else:
            print("Люк Скайуокер не найден в базе")

    finally:
        # Корректное закрытие соединения
        await conn.close()


if __name__ == '__main__':
    asyncio.run(check_data())
