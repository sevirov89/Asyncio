import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
# Это позволяет хранить конфиденциальные данные отдельно от кода
load_dotenv()

DB_CONFIG = {
    'user': os.getenv('DB_USER', 'your_username'),
    'password': os.getenv('DB_PASSWORD', 'your_password'),
    'database': os.getenv('DB_NAME', 'your_database'),
    'host': os.getenv('DB_HOST', 'localhost')
}