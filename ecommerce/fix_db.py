import sqlite3

# Connect to your SQLite database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Query to get the schema of the shop_cart table
query = "PRAGMA table_info(shop_cart);"
cursor.execute(query)
columns = cursor.fetchall()
print("Columns in shop_cart:", columns)

# Close the connection
conn.close()
