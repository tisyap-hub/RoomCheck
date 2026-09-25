import sys
from pathlib import Path

import pandas as pd

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

from validator import (
    validate_columns,
    clean_timetable
)


def test_validate_columns_success():

    df = pd.DataFrame({
        "Day": ["Monday"],
        "Start": ["09:00"],
        "End": ["10:00"],
        "Room": ["A101"],
        "Teacher": ["John"],
        "Subject": ["Math"],
        "Class": ["CSE-A"]
    })

    valid, missing_columns = validate_columns(df)

    assert valid is True
    assert missing_columns == []


def test_validate_columns_missing_column():

    df = pd.DataFrame({
        "Day": ["Monday"],
        "Start": ["09:00"],
        "End": ["10:00"],
        "Room": ["A101"],
        "Teacher": ["John"],
        "Subject": ["Math"]
    })

    valid, missing_columns = validate_columns(df)

    assert valid is False
    assert "Class" in missing_columns


def test_clean_timetable():

    df = pd.DataFrame({
        "Day": [" Monday "],
        "Start": ["09:00"],
        "End": ["10:00"],
        "Room": [" a101 "],
        "Teacher": [" John "],
        "Subject": [" Mathematics "],
        "Class": [" CSE-A "]
    })

    cleaned = clean_timetable(df)

    assert cleaned.loc[0, "Day"] == "Monday"
    assert cleaned.loc[0, "Room"] == "A101"
    assert cleaned.loc[0, "Teacher"] == "John"
    assert cleaned.loc[0, "Subject"] == "Mathematics"
    assert cleaned.loc[0, "Class"] == "CSE-A"