\# RoomCheck — Classroom Conflict Detector



RoomCheck is a Python-based timetable analysis application that detects classroom and teacher scheduling conflicts.



It allows users to upload a timetable spreadsheet, analyze the schedule, identify conflicts, and find possible alternative classrooms.



\## Features



\- Upload Excel (`.xlsx`) or CSV timetable files

\- Validate timetable columns

\- Clean timetable data

\- Detect room clashes

\- Detect teacher clashes

\- Detect unavailable classrooms

\- Explain detected conflicts

\- Suggest alternative rooms based on:

&#x20; - Room availability

&#x20; - Room capacity

&#x20; - Existing timetable occupancy

\- Filter timetable data by day, room, and teacher

\- Search by class or subject

\- View conflict summaries

\- Download conflict reports as CSV

\- Automated testing with pytest



\## Tech Stack



\- Python

\- Pandas

\- SQLite

\- Streamlit

\- OpenPyXL

\- Pytest



\## Project Structure



```text

RoomCheck/

│

├── data/

│   └── timetable.xlsx

│

├── tests/

│   ├── test\_validator.py

│   ├── test\_conflict\_detector.py

│   ├── test\_room\_suggestions.py

│   └── test\_edge\_cases.py

│

├── app.py

├── validator.py

├── conflict\_detector.py

├── database.py

├── room\_suggestions.py

├── requirements.txt

├── .gitignore

└── README.md

