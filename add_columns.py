"""
Quick script to add server_a_status and server_b_status columns
to the requests table for the 3-step approval chain.
"""
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='databreach'
)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE requests ADD COLUMN server_a_status VARCHAR(20) DEFAULT 'pending'")
    print("[OK] Column server_a_status added successfully!")
except Exception as e:
    print(f"[SKIP] server_a_status: {e}")

try:
    cursor.execute("ALTER TABLE requests ADD COLUMN server_b_status VARCHAR(20) DEFAULT 'pending'")
    print("[OK] Column server_b_status added successfully!")
except Exception as e:
    print(f"[SKIP] server_b_status: {e}")

conn.commit()
cursor.close()
conn.close()
print("\nDone! Both columns are now in the requests table.")
