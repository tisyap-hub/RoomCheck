import sys
from pathlib import Path

import pandas as pd

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

from conflict_detector import (
    time_overlap,
    detect_conflicts,
    prepare_times
)


def test_time_overlap():

    assert time_overlap(
        "09:00",
        "10:00",
        "09:30",
        "10:30"
    ) is True


def test_no_time_overlap():

    assert time_overlap(
        "09:00",
        "10:00",
        "10:00",
        "11:00"
    ) is False


def test_room_clash():

    df = pd.DataFrame({
        "Day": ["Monday", "Monday"],
        "Start": ["09:00", "09:30"],
        "End": ["10:00", "10:30"],
        "Room": ["A101", "A101"],
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

    assert len(room_clashes) == 1


def test_teacher_clash():

    df = pd.DataFrame({
        "Day": ["Monday", "Monday"],
        "Start": ["09:00", "09:30"],
        "End": ["10:00", "10:30"],
        "Room": ["A101", "A102"],
        "Teacher": ["John", "John"],
        "Subject": ["Math", "Physics"],
        "Class": ["CSE-A", "CSE-B"]
    })

    df = prepare_times(df)

    conflicts = detect_conflicts(df)

    teacher_clashes = [
        conflict
        for conflict in conflicts
        if conflict["type"] == "Teacher Clash"
    ]

    assert len(teacher_clashes) == 1


def test_no_conflict():

    df = pd.DataFrame({
        "Day": ["Monday", "Monday"],
        "Start": ["09:00", "10:00"],
        "End": ["10:00", "11:00"],
        "Room": ["A101", "A101"],
        "Teacher": ["John", "John"],
        "Subject": ["Math", "Physics"],
        "Class": ["CSE-A", "CSE-B"]
    })

    df = prepare_times(df)

    conflicts = detect_conflicts(df)

    assert conflicts == []