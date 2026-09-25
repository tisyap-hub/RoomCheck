import sqlite3


DATABASE_NAME = "roomcheck.db"


def create_database():
    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name TEXT UNIQUE NOT NULL,
            capacity INTEGER NOT NULL,
            available INTEGER NOT NULL DEFAULT 1
        )
    """)

    connection.commit()
    connection.close()


def add_sample_rooms():
    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    rooms = [
        ("A101", 60, 1),
        ("A102", 40, 1),
        ("A103", 30, 0),
        ("A104", 100, 1),
        ("A105", 60, 1)
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO rooms
        (room_name, capacity, available)
        VALUES (?, ?, ?)
    """, rooms)

    connection.commit()
    connection.close()


def get_available_rooms():
    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT room_name, capacity
        FROM rooms
        WHERE available = 1
    """)

    rooms = cursor.fetchall()

    connection.close()

    return rooms

def get_room_status(room_name):
    """
    Get the capacity and availability status of a room.
    """

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT room_name, capacity, available
        FROM rooms
        WHERE room_name = ?
    """, (room_name,))

    room = cursor.fetchone()

    connection.close()

    return room


if __name__ == "__main__":

    create_database()

    add_sample_rooms()

    print("Database created successfully.")

    print("\nAvailable rooms:")

    rooms = get_available_rooms()

    for room in rooms:
        print(room)