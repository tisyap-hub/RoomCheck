import pandas as pd

from database import get_room_status

def time_overlap(start1, end1, start2, end2):
    """
    Check whether two time periods overlap.
    """

    return start1 < end2 and start2 < end1


def prepare_times(df):
    """
    Convert Start and End columns into time values.
    """

    df = df.copy()

    df["Start"] = pd.to_datetime(
        df["Start"].astype(str),
        format="mixed"
    ).dt.time

    df["End"] = pd.to_datetime(
        df["End"].astype(str),
        format="mixed"
    ).dt.time

    return df

def detect_unavailable_rooms(df):
    """
    Detect classes assigned to unavailable rooms.
    """

    conflicts = []

    for _, row in df.iterrows():

        room = row["Room"]

        room_status = get_room_status(room)

        # Room does not exist in database
        if room_status is None:
            continue

        room_name, capacity, available = room_status

        # Room is marked unavailable
        if available == 0:

            conflicts.append({
                "type": "Unavailable Room",
                "day": row["Day"],
                "start": row["Start"],
                "end": row["End"],
                "room": room_name,
                "details": (
                    f"Room {room_name} is unavailable, "
                    f"but it is assigned to {row['Class']} "
                    f"for {row['Subject']}."
                )
            })

    return conflicts


def detect_conflicts(df):
    """
    Detect room clashes and teacher clashes.
    """

    df = prepare_times(df)

    conflicts = []

    for i in range(len(df)):

        for j in range(i + 1, len(df)):

            row1 = df.iloc[i]
            row2 = df.iloc[j]

            # Only compare classes on the same day
            if row1["Day"].lower() != row2["Day"].lower():
                continue

            # Ignore classes that don't overlap in time
            if not time_overlap(
                row1["Start"],
                row1["End"],
                row2["Start"],
                row2["End"]
            ):
                continue

            # -------------------------
            # ROOM CLASH
            # -------------------------

            if row1["Room"] == row2["Room"]:

                conflicts.append({
                    "type": "Room Clash",
                    "day": row1["Day"],
                    "start": row1["Start"],
                    "end": row1["End"],
                    "room": row1["Room"],
                    "details": (
                        f"Room {row1['Room']} is assigned to "
                        f"{row1['Class']} and {row2['Class']} "
                        f"at the same time."
                    )
                })

            # -------------------------
            # TEACHER CLASH
            # -------------------------

            if row1["Teacher"].lower() == row2["Teacher"].lower():

                conflicts.append({
                    "type": "Teacher Clash",
                    "day": row1["Day"],
                    "start": row1["Start"],
                    "end": row1["End"],
                    "room": (
                        f"{row1['Room']} / {row2['Room']}"
                    ),
                    "details": (
                        f"Teacher {row1['Teacher']} is assigned "
                        f"to two classes at the same time."
                    )
                })

    return conflicts

if __name__ == "__main__":

    from validator import load_timetable, clean_timetable

    file_path = "data/timetable.xlsx"

    timetable = load_timetable(file_path)

    timetable = clean_timetable(timetable)

    # Detect room and teacher clashes
    conflicts = detect_conflicts(timetable)

    # Detect unavailable rooms
    unavailable_rooms = detect_unavailable_rooms(timetable)

    print("\nCONFLICTS FOUND:")
    print("----------------")

    for conflict in conflicts:

        print(f"\nType: {conflict['type']}")
        print(f"Day: {conflict['day']}")
        print(f"Time: {conflict['start']} - {conflict['end']}")
        print(f"Room: {conflict['room']}")
        print(f"Details: {conflict['details']}")

    print("\nUNAVAILABLE ROOMS:")
    print("------------------")

    if unavailable_rooms:

        for conflict in unavailable_rooms:

            print(f"\nType: {conflict['type']}")
            print(f"Day: {conflict['day']}")
            print(f"Time: {conflict['start']} - {conflict['end']}")
            print(f"Room: {conflict['room']}")
            print(f"Details: {conflict['details']}")

    else:

        print("No unavailable rooms found.")