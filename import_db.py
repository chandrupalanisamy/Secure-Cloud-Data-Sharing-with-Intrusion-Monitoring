import mysql.connector

try:
    # Connect without DB to create it
    conn = mysql.connector.connect(host='localhost', user='root', password='')
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS databreach;")
    conn.commit()
    cursor.close()
    conn.close()
    print("Database databreach ensured.")

    # Connect to the new DB and import SQL
    conn = mysql.connector.connect(host='localhost', user='root', password='', database='databreach')
    cursor = conn.cursor()
    
    with open('databreach.sql', 'r') as f:
        sql_file = f.read()
    
    statements = sql_file.split(';')
    for statement in statements:
        if statement.strip():
            cursor.execute(statement)
    conn.commit()
    print("Imported databreach.sql successfully.")

except Exception as e:
    print(f"Error: {e}")
finally:
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
