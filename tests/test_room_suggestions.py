import sys
from pathlib import Path

import pandas as pd

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

from room_suggestions import suggest_rooms


def test_suggest_available_room():

    timetable = pd.DataFrame({
        "Day": ["Monday"],
        "Start": ["09:00"],
        "End": ["10:00"],
        "Room": ["A101"],
        "Teacher": ["John"],
        "Subject": ["Math"],
        "Class": ["CSE-A"]
    })

    suggestions = suggest_rooms(
        required_capacity=30,
        day="Monday",
        start="10:00",
        end="11:00",
        timetable=timetable
    )

    room_names = [
        room[0]
        for room in suggestions
    ]

    assert "A102" in room_names
    assert "A103" not in room_names


def test_do_not_suggest_occupied_room():

    timetable = pd.DataFrame({
        "Day": ["Monday"],
        "Start": ["09:00"],
        "End": ["10:00"],
        "Room": ["A101"],
        "Teacher": ["John"],
        "Subject": ["Math"],
        "Class": ["CSE-A"]
    })

    suggestions = suggest_rooms(
        required_capacity=30,
        day="Monday",
        start="09:30",
        end="10:30",
        timetable=timetable
    )

    room_names = [
        room[0]
        for room in suggestions
    ]

    assert "A101" not in room_names


def test_capacity_requirement():

    timetable = pd.DataFrame({
        "Day": ["Monday"],
        "Start": ["09:00"],
        "End": ["10:00"],
        "Room": ["A101"],
        "Teacher": ["John"],
        "Subject": ["Math"],
        "Class": ["CSE-A"]
    })

    suggestions = suggest_rooms(
        required_capacity=80,
        day="Monday",
        start="10:00",
        end="11:00",
        timetable=timetable
    )

    room_names = [
        room[0]
        for room in suggestions
    ]

    assert "A104" in room_names
    assert "A101" not in room_names
    assert "A102" not in room_names
    assert "A105" not in room_names