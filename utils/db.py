import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('history.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы, если она не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        count INTEGER
    )
''')
conn.commit()


def insert_history(timestamp, count):
    """
    Сохраняет результат обработки в историю.
    
    :param timestamp: Время запроса (datetime.now())
    :param count: Количество найденных объектов
    """
    cursor.execute('''
        INSERT INTO requests (timestamp, count)
        VALUES (?, ?)
    ''', (timestamp, count))
    conn.commit()


def get_last_result():
    """
    Возвращает последнюю запись из истории.
    
    :return: кортеж (timestamp, count) или None, если записей нет
    """
    cursor.execute('''
        SELECT timestamp, count
        FROM requests
        ORDER BY id DESC
        LIMIT 1
    ''')
    return cursor.fetchone()