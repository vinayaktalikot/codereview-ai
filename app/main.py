import os
import sqlite3

def get_user_data(user_id: int):
    """
    Retrieves user data from the database for a given user ID.
    """
    db_path = os.getenv("DATABASE_PATH", "users.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT username, email FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))

    user_data = cursor.fetchone()
    conn.close()

    return user_data

if __name__ == "__main__":
    user = get_user_data(1)
    if user:
        print(f"Username: {user[0]}, Email: {user[1]}")
    else:
        print("User not found.")