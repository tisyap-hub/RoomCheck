import sqlite3
import pandas as pd

from database import DATABASE_NAME


def convert_to_time(value):
    """
    Convert a timetable time value into datetime.time.
    """

    if hasattr(value, "hour"):
        return value

    return pd.to_datetime(
        str(value),
        format="mixed"
    ).time()


def suggest_rooms(
    required_capacity,
    day,
    start,
    end,
    timetable
):
    """
    Suggest available rooms that:
    1. Have enough capacity.
    2. Are not already occupied at the given time.
    """

    # Convert requested conflict time
    start = convert_to_time(start)
    end = convert_to_time(end)

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    cursor = connection.cursor()

    cursor.execute("""
        SELECT room_name, capacity
        FROM rooms
        WHERE available = 1
        AND capacity >= ?
        ORDER BY capacity ASC
    """, (required_capacity,))

    available_rooms = cursor.fetchall()

    connection.close()

    suggestions = []

    for room_name, capacity in available_rooms:

        room_is_occupied = False

        for _, row in timetable.iterrows():

            # Different day
            if str(row["Day"]).lower() != str(day).lower():
                continue

            # Different room
            if str(row["Room"]).upper() != str(room_name).upper():
                continue

            # Convert timetable times
            row_start = convert_to_time(
                row["Start"]
            )

            row_end = convert_to_time(
                row["End"]
            )

            # Check time overlap
            if (
                start < row_end
                and row_start < end
            ):

                room_is_occupied = True

                break

        if not room_is_occupied:

            suggestions.append(
                (room_name, capacity)
            )

    return suggestions