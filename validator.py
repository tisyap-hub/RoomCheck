import pandas as pd


REQUIRED_COLUMNS = [
    "Day",
    "Start",
    "End",
    "Room",
    "Teacher",
    "Subject",
    "Class"
]


def load_timetable(file):
    """Load a timetable from Excel or CSV."""

    if file.lower().endswith(".csv"):
        return pd.read_csv(file)

    if file.lower().endswith(".xlsx"):
        return pd.read_excel(file)

    raise ValueError("Only CSV and Excel files are supported.")


def validate_columns(df):
    """Check whether all required columns exist."""

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        return False, missing_columns

    return True, []


def clean_timetable(df):
    """Clean timetable text values."""

    df = df.copy()

    text_columns = [
        "Day",
        "Room",
        "Teacher",
        "Subject",
        "Class"
    ]

    for column in text_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    df["Room"] = df["Room"].str.upper()

    return df