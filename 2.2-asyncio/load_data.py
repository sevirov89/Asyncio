import aiohttp
import asyncpg
import asyncio
from config import DB_CONFIG


BASE_URL = "https://www.swapi.tech/api/people/"
# Максимальное количество одновременных соединений с БД
# Ограничивает параллельные INSERT-операции для предотвращения перегрузки
DB_POOL_SIZE = 10


async def get_max_id(session):
    async with session.get(BASE_URL) as response:
        try:
            if response.status == 200:
                data = await response.json()
                return data['total_records']
            else:
                print(f"Ошибка определения max_id {BASE_URL}")
        except Exception as e:
            print(f"Ошибка запроса max_id {BASE_URL}")
            print(e)
            return None


async def fetch_character(session, character_id):
    url = f"{BASE_URL}{character_id}"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return data.get('result', {}).get('properties')
        return None


async def insert_character(conn, character_data, character_id):
    if not character_data:
        return

    await conn.execute('''
        INSERT INTO star_wars_people (
            id, birth_year, eye_color, gender, hair_color,
            homeworld, mass, name, skin_color
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (id) DO NOTHING
    ''',
                       character_id,
                       character_data.get('birth_year'),
                       character_data.get('eye_color'),
                       character_data.get('gender'),
                       character_data.get('hair_color'),
                       character_data.get('homeworld'),
                       character_data.get('mass'),
                       character_data.get('name'),
                       character_data.get('skin_color'))


async def process_character(session, pool, character_id):
    try:
        character_data = await fetch_character(session, character_id)
        if character_data:
            # Берем соединение из пула только на время выполнения INSERT
            # Это гарантирует, что каждая операция записи использует
            # собственное соединение, предотвращая конфликты при конкурентном доступе
            async with pool.acquire() as conn:
                await insert_character(conn, character_data, character_id)
            print(f"Обработка персонажа {character_id}")
        else:
            print(f"Персонаж {character_id} не найден")
    except Exception as e:
        print(f"Ошибка обработки персонажа {character_id}: {e}")


async def main():
    # Создаем пул соединений вместо одного соединения
    # Пул автоматически управляет соединениями и ограничивает
    # количество одновременных операций с БД
    pool = await asyncpg.create_pool(
        **DB_CONFIG,
        min_size=DB_POOL_SIZE,
        max_size=DB_POOL_SIZE
    )
    try:
        async with aiohttp.ClientSession() as session:
            max_id = await get_max_id(session)
            tasks = []
            for character_id in range(1, max_id + 1):
                # Передаем пул вместо отдельного соединения
                task = asyncio.create_task(process_character(session, pool, character_id))
                tasks.append(task)

            await asyncio.gather(*tasks)
    finally:
        # Корректно закрываем пул соединений
        await pool.close()


if __name__ == '__main__':
    asyncio.run(main())