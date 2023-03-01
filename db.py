import sqlite3


def create_db():
  conn = None
  try:
    conn = sqlite3.connect('catalog.db')
    c = conn.cursor()
    c.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price REAL,
                image_url TEXT
            )
        ''')
    c.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
    c.execute('''
            CREATE TABLE IF NOT EXISTS item_tags (
                item_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id)
            )
        ''')
    c.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_item_tags
            ON item_tags (item_id, tag_id)
        ''')
    conn.commit()
    c.close()
  except sqlite3.Error as e:
    print(e)
  finally:
    if conn:
      conn.close()


import random

def populate_db():
    conn = None
    try:
        conn = sqlite3.connect('catalog.db')
        c = conn.cursor()
        # Insert example items
        items = [
            ('Item 1', 'Description of item 1', 9.99, 'https://example.com/item1.jpg'),
            ('Item 2', 'Description of item 2', 14.99, 'https://example.com/item2.jpg'),
            ('Item 3', 'Description of item 3', 19.99, 'https://example.com/item3.jpg'),
            ('Item 4', 'Description of item 4', 24.99, 'https://example.com/item4.jpg'),
            ('Item 5', 'Description of item 5', 29.99, 'https://example.com/item5.jpg'),
        ]
        c.executemany('INSERT INTO items (name, description, price, image_url) VALUES (?, ?, ?, ?)', items)
        conn.commit()
        
        # Insert example tags
        tags = [
            'Tag 1',
            'Tag 2',
            'Tag 3',
            'Tag 4',
            'Tag 5',
        ]
        c.executemany('INSERT INTO tags (name) VALUES (?)', [(tag,) for tag in tags])
        conn.commit()
        
        # Associate tags with items
        item_ids = [item[0] for item in c.execute('SELECT id FROM items').fetchall()]
        tag_ids = [tag[0] for tag in c.execute('SELECT id FROM tags').fetchall()]
        item_tags = []
        for item_id in item_ids:
            item_tags.extend(random.sample(tag_ids, k=random.randint(1, len(tag_ids))))
        c.executemany('INSERT INTO item_tags (item_id, tag_id) VALUES (?, ?)', [(item_id, tag_id) for item_id in item_ids for tag_id in item_tags])
        conn.commit()
        c.close()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
