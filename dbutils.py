import sqlite3, logging

DATABASE = 'data.db'

def get_cursor():
    return get_db_connection().cursor()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    #conn.row_factory = sqlite3.Row  # Enable access to columns by name
    return conn

def db_setup():
    lg = logging.getLogger()

    conn = get_db_connection()
    cursor = conn.cursor()

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
            is_primary INTEGER NOT NULL CHECK (is_primary IN (0, 1)),
            FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
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
        images = [
            # Item 1
            (1, "item1_primary.jpg", 1),  # Primary image
            (1, "item1_alt1.jpg", 0),
            (1, "item1_alt2.jpg", 0),
            # Item 2
            (2, "item2_primary.jpg", 1),  # Primary image
            (2, "item2_alt1.jpg", 0),
            # Item 3
            (3, "item3_primary.jpg", 1),  # Primary image
            (3, "item3_alt1.jpg", 0),
            (3, "item3_alt2.jpg", 0),
            # Item 4
            (4, "item4_primary.jpg", 1),  # Primary image
        ]
        cursor.executemany('INSERT INTO images (item_id, image_name, is_primary) VALUES (?, ?, ?)', images)

    lg.info("Database seeded with initial data.")

    conn.commit()
    conn.close()