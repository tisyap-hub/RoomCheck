import sys
from pathlib import Path

import pandas as pd

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

from conflict_detector import (
    detect_conflicts,
    prepare_times
)


def test_classes_touching_not_overlap():

    df = pd.DataFrame({
        "Day": ["Monday", "Monday"],
        "Start": ["09:00", "10:00"],
        "End": ["10:00", "11:00"],
        "Room": ["A101", "A101"],
        "Teacher": ["John", "Sarah"],
        "Subject": ["Math", "Physics"],
        "Class": ["CSE-A", "CSE-B"]
    })

    df = prepare_times(df)

    conflicts = detect_conflicts(df)

    assert conflicts == []


def test_different_days_no_conflict():

    df = pd.DataFrame({
        "Day": ["Monday", "Tuesday"],
        "Start": ["09:00", "09:00"],
        "End": ["10:00", "10:00"],
        "Room": ["A101", "A101"],
        "Teacher": ["John", "John"],
        "Subject": ["Math", "Physics"],
        "Class": ["CSE-A", "CSE-B"]
    })

    df = prepare_times(df)

    conflicts = detect_conflicts(df)

    assert conflicts == []


def test_different_rooms_no_room_clash():

    df = pd.DataFrame({
        "Day": ["Monday", "Monday"],
        "Start": ["09:00", "09:00"],
        "End": ["10:00", "10:00"],
        "Room": ["A101", "A102"],
        "Teacher": ["John", "Sarah"],
        "Subject": ["Math", "Physics"],
        "Class": ["CSE-A", "CSE-B"]
    })

    df = prepare_times(df)

    conflicts = detect_conflicts(df)

    room_clashes = [
        conflict
        for conflict in conflicts
        if conflict["type"] == "Room Clash"
    ]

    assert room_clashes == []