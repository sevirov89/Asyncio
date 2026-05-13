import asyncpg
import asyncio
from config import DB_CONFIG

async def create_table():
    conn = await asyncpg.connect(**DB_CONFIG)
    try:
        await conn.execute('''
            CREATE TABLE star_wars_people (
                id INTEGER PRIMARY KEY,
                birth_year TEXT,
                eye_color TEXT,
                gender TEXT,
                hair_color TEXT,
                homeworld TEXT,
                mass TEXT,
                name TEXT,
                skin_color TEXT
            )
        ''')
        print("Таблица успешно создана")
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(create_table())