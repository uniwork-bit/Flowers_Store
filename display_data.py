import sqlite3

# Connect to the database
conn = sqlite3.connect('flowers_store.db')
cursor = conn.cursor()

# Display Categories
print("Categories table:")
cursor.execute('SELECT * FROM Categories')
categories = cursor.fetchall()
for cat in categories:
    print(f"ID: {cat[0]}, Name: {cat[1]}")

print("\nFlowers table:")
cursor.execute('SELECT f.id, f.name, c.name, f.price, f.stock, f.description FROM Flowers f JOIN Categories c ON f.category_id = c.id')
flowers = cursor.fetchall()
for flower in flowers:
    print(f"ID: {flower[0]}, Name: {flower[1]}, Category: {flower[2]}, Price: {flower[3]}, Stock: {flower[4]}, Description: {flower[5]}")

# Close the connection
conn.close()