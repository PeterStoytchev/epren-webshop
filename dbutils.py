import shutil
import sqlite3
import logging
import uuid
from contextlib import contextmanager

DATABASE = 'data.db'

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    try:
        conn.execute('PRAGMA foreign_keys = ON')  # Enable foreign key constraints
        yield conn
        conn.commit()
    finally:
        conn.close()

@contextmanager
def get_cursor():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

def db_setup():
    with get_cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                description TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                image_name TEXT NOT NULL,
                slot INTEGER NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                total REAL NOT NULL,
                description TEXT NOT NULL
            )
        ''')

        # Seed the database with some example data if there is none (only for development)
        cursor.execute('SELECT COUNT(*) FROM items')
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                INSERT INTO items (title, price, quantity, description) VALUES (?, ?, ?, ?)
            ''', [
                ('Item 1', 10.99, 100, "This is item 1"),
                ('Item 2', 15.49, 50, "This is item 2"),
                ('Item 3', 7.25, 200, "This is item 3"),
                ('Item 4', 12.00, 75, "This is item 4")
            ])

        cursor.execute('SELECT COUNT(*) FROM images')
        if cursor.fetchone()[0] == 0:
            new_names = []
            for i in range(9):
                new_name = f"{str(uuid.uuid4())}.png"
                shutil.copyfile("static/images/default.png", f"static/images/{new_name}")
                new_names.append(new_name)
            
            images = [
                # Item 1
                (1, new_names[0], 1),
                (1, new_names[1], 2),
                (1, new_names[2], 3),
                # Item 2
                (2, new_names[3], 1),
                (2, new_names[4], 2),
                # Item 3
                (3, new_names[5], 1),
                (3, new_names[6], 2),
                (3, new_names[7], 3),
                # Item 4
                (4, new_names[8], 1),
            ]
            cursor.executemany('INSERT INTO images (item_id, image_name, slot) VALUES (?, ?, ?)', images)

        cursor.execute('SELECT COUNT(*) FROM orders')
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                INSERT INTO orders (customer_id, total, description) VALUES (?, ?, ?)
            ''', [
                (0, 19.99, "This is order 1"),
                (0, 99.49, "This is order 2"),
                (0, 106.25, "This is order 3"),
                (0, 123.00, "This is order 4")
            ])


        logging.info("Database seeded with initial data.")