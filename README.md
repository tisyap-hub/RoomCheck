# RoomCheck — Classroom Conflict Detector

RoomCheck is a Python-based timetable analysis application that detects classroom and teacher scheduling conflicts.

The application allows users to upload a timetable spreadsheet, validate and analyze the schedule, identify conflicts, and find suitable alternative classrooms.

## Features

- Upload Excel (`.xlsx`) or CSV timetable files
- Validate required timetable columns
- Clean and standardize timetable data
- Detect classroom/room clashes
- Detect teacher scheduling clashes
- Detect unavailable classrooms
- Explain detected conflicts
- Suggest alternative classrooms based on:
  - Room availability
  - Room capacity
  - Existing timetable occupancy
- Filter timetable data by:
  - Day
  - Room
  - Teacher
- Search timetable data by class or subject
- View conflict summaries
- Download conflict reports as CSV
- Automated testing using Pytest
- SQLite database for classroom information

## Tech Stack

- **Python** — Core programming language
- **Pandas** — Timetable data processing and analysis
- **SQLite** — Classroom database
- **Streamlit** — Web application interface
- **OpenPyXL** — Excel file handling
- **Pytest** — Automated testing

## Project Structure

```text
RoomCheck/
│
├── data/
│   └── timetable.xlsx
│
├── tests/
│   ├── test_validator.py
│   ├── test_conflict_detector.py
│   ├── test_room_suggestions.py
│   └── test_edge_cases.py
│
├── app.py
├── validator.py
├── conflict_detector.py
├── database.py
├── room_suggestions.py
├── requirements.txt
├── .gitignore
└── README.md