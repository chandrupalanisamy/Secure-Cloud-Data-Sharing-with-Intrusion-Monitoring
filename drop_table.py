import mysql.connector

try:
    conn = mysql.connector.connect(host='localhost', user='root', password='', database='databreach')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS malware_links;")
    conn.commit()
    print("Table malware_links dropped successfully.")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
