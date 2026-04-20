import sqlite3

# Connect to SQLite database (creates the file if it doesn't exist)
conn = sqlite3.connect('flowers_store.db')
cursor = conn.cursor()

# Create Categories table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
''')

# Create Flowers table with Foreign Key
cursor.execute('''
CREATE TABLE IF NOT EXISTS Flowers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER,
    price REAL NOT NULL,
    stock INTEGER NOT NULL,
    description TEXT,
    FOREIGN KEY (category_id) REFERENCES Categories(id)
)
''')

# Insert sample data into Categories
categories_data = [
    ('Seasonal',),
    ('Exotic',),
    ('Local',)
]

cursor.executemany('INSERT INTO Categories (name) VALUES (?)', categories_data)

# Insert sample data into Flowers
flowers_data = [
    ('Rose', 1, 50.0, 100, 'Red rose'),
    ('Tulip', 1, 40.0, 80, 'Yellow tulip'),
    ('Orchid', 2, 100.0, 50, 'Rare orchid'),
    ('Sunflower', 3, 30.0, 200, 'Bright sunflower'),
    ('Lily', 1, 60.0, 70, 'White lily')
]

cursor.executemany('INSERT INTO Flowers (name, category_id, price, stock, description) VALUES (?, ?, ?, ?, ?)', flowers_data)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database created successfully with tables and sample data.")