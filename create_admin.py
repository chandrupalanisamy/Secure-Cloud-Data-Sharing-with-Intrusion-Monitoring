import mysql.connector

try:
    conn = mysql.connector.connect(host='localhost', user='root', password='', database='databreach')
    cursor = conn.cursor()
    # Check if admin user already exists
    cursor.execute("SELECT * FROM user WHERE name='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO user (name, password, status, email) VALUES ('admin', 'admin', 'allowed', 'admin@example.com')")
        conn.commit()
        print("User 'admin' created in database.")
    else:
        print("User 'admin' already exists.")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
