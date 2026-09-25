import streamlit as st
import pandas as pd

from validator import (
    validate_columns,
    clean_timetable
)

from conflict_detector import (
    detect_conflicts,
    detect_unavailable_rooms,
    prepare_times
)

from room_suggestions import suggest_rooms


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="RoomCheck",
    page_icon="🏫",
    layout="wide"
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🏫 RoomCheck")

    st.write(
        "Classroom timetable conflict detector."
    )

    st.divider()

    st.subheader("What RoomCheck detects")

    st.write("🏠 Room clashes")
    st.write("👨‍🏫 Teacher clashes")
    st.write("🚫 Unavailable rooms")
    st.write("💡 Alternative rooms")

    st.divider()

    st.caption(
        "Upload a timetable to begin."
    )


# =========================================================
# MAIN HEADER
# =========================================================

st.title("🏫 RoomCheck")

st.markdown(
    "### Classroom Conflict Detection System"
)

st.write(
    "Upload your timetable and automatically identify "
    "room conflicts, teacher conflicts, unavailable "
    "classrooms, and possible alternative rooms."
)


# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "📁 Upload timetable",
    type=["xlsx", "csv"],
    help="Supported formats: Excel (.xlsx) and CSV (.csv)"
)


if uploaded_file is None:

    st.info(
        "👆 Upload an Excel or CSV timetable to start."
    )

    st.stop()


# =========================================================
# LOAD FILE
# =========================================================

try:

    if uploaded_file.name.lower().endswith(".csv"):

        timetable = pd.read_csv(uploaded_file)

    else:

        timetable = pd.read_excel(uploaded_file)


except Exception as error:

    st.error(
        f"Unable to read the uploaded file: {error}"
    )

    st.stop()


# =========================================================
# VALIDATE FILE
# =========================================================

valid, missing_columns = validate_columns(
    timetable
)


if not valid:

    st.error(
        "❌ This timetable does not have the required columns."
    )

    st.write("Missing columns:")

    for column in missing_columns:

        st.write(f"- `{column}`")

    st.stop()


# =========================================================
# CLEAN DATA
# =========================================================

timetable = clean_timetable(
    timetable
)


# =========================================================
# PREPARE TIME DATA
# =========================================================

timetable_for_suggestions = prepare_times(
    timetable
)


st.success(
    f"✅ Successfully loaded `{uploaded_file.name}`"
)


# =========================================================
# DETECT CONFLICTS
# =========================================================

conflicts = detect_conflicts(
    timetable
)

unavailable_rooms = detect_unavailable_rooms(
    timetable
)


# =========================================================
# ROW STATUS FUNCTION
# =========================================================

def get_row_status(row):

    row_day = str(
        row["Day"]
    ).lower()

    row_room = str(
        row["Room"]
    ).upper()

    row_teacher = str(
        row["Teacher"]
    ).lower()


    # Convert row start time

    row_start = pd.to_datetime(
        str(row["Start"]),
        format="mixed"
    ).time()


    # Convert row end time

    row_end = pd.to_datetime(
        str(row["End"]),
        format="mixed"
    ).time()


    # -----------------------------------------
    # UNAVAILABLE ROOM
    # -----------------------------------------

    for conflict in unavailable_rooms:

        conflict_day = str(
            conflict["day"]
        ).lower()

        conflict_room = str(
            conflict["room"]
        ).upper()

        conflict_start = pd.to_datetime(
            str(conflict["start"]),
            format="mixed"
        ).time()


        if (
            conflict_day == row_day
            and conflict_room == row_room
            and conflict_start == row_start
        ):

            return "🚫 Unavailable Room"


    # -----------------------------------------
    # ROOM / TEACHER CONFLICTS
    # -----------------------------------------

    for conflict in conflicts:

        if str(
            conflict["day"]
        ).lower() != row_day:

            continue


        conflict_start = pd.to_datetime(
            str(conflict["start"]),
            format="mixed"
        ).time()


        conflict_end = pd.to_datetime(
            str(conflict["end"]),
            format="mixed"
        ).time()


        # Check whether the times overlap

        if not (
            row_start < conflict_end
            and conflict_start < row_end
        ):

            continue


        # -----------------------------------------
        # ROOM CLASH
        # -----------------------------------------

        if conflict["type"] == "Room Clash":

            if str(
                conflict["room"]
            ).upper() == row_room:

                return "🔴 Room Clash"


        # -----------------------------------------
        # TEACHER CLASH
        # -----------------------------------------

        if conflict["type"] == "Teacher Clash":

            if row_teacher in str(
                conflict["details"]
            ).lower():

                return "🟠 Teacher Clash"


    # -----------------------------------------
    # NO PROBLEM
    # -----------------------------------------

    return "🟢 OK"


# =========================================================
# ADD STATUS TO TIMETABLE
# =========================================================

timetable["Status"] = timetable.apply(
    get_row_status,
    axis=1
)


# =========================================================
# SEPARATE CONFLICT TYPES
# =========================================================

room_conflicts = [
    conflict
    for conflict in conflicts
    if conflict["type"] == "Room Clash"
]


teacher_conflicts = [
    conflict
    for conflict in conflicts
    if conflict["type"] == "Teacher Clash"
]


# =========================================================
# TOTAL CONFLICTS
# =========================================================

total_conflicts = (
    len(room_conflicts)
    + len(teacher_conflicts)
    + len(unavailable_rooms)
)


# =========================================================
# DASHBOARD METRICS
# =========================================================

st.subheader(
    "📊 Conflict Dashboard"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Conflicts",
        total_conflicts
    )


with col2:

    st.metric(
        "🏠 Room Clashes",
        len(room_conflicts)
    )


with col3:

    st.metric(
        "👨‍🏫 Teacher Clashes",
        len(teacher_conflicts)
    )


with col4:

    st.metric(
        "🚫 Unavailable Rooms",
        len(unavailable_rooms)
    )

# =========================================================
# CONFLICT SUMMARY
# =========================================================

st.subheader("📈 Conflict Summary")

if total_conflicts == 0:

    st.info(
        "No conflicts available for summary."
    )

else:

    summary_rows = []

    for conflict in conflicts:

        summary_rows.append({
            "Day": conflict["day"],
            "Type": conflict["type"]
        })

    for conflict in unavailable_rooms:

        summary_rows.append({
            "Day": conflict["day"],
            "Type": conflict["type"]
        })

    summary_df = pd.DataFrame(
        summary_rows
    )

    if not summary_df.empty:

        daily_summary = (
            summary_df
            .groupby("Day")
            .size()
            .reset_index(name="Conflicts")
        )

        daily_summary = daily_summary.sort_values(
            "Conflicts",
            ascending=False
        )

        st.write(
            "Number of detected issues by day:"
        )

        st.dataframe(
            daily_summary,
            use_container_width=True,
            hide_index=True
        )

        st.bar_chart(
            daily_summary.set_index("Day")
        )

st.divider()


# =========================================================
# OVERALL STATUS
# =========================================================

if total_conflicts == 0:

    st.success(
        "🎉 No conflicts were detected in this timetable!"
    )

else:

    st.warning(
        f"⚠️ RoomCheck found {total_conflicts} "
        "potential issue(s)."
    )


# =========================================================
# TIMETABLE EXPLORER
# =========================================================

st.subheader(
    "📅 Timetable Explorer"
)

st.write(
    "Filter the timetable by day, room, teacher, "
    "class, or subject."
)


# =========================================================
# FILTER OPTIONS
# =========================================================

filter_col1, filter_col2, filter_col3 = st.columns(3)


with filter_col1:

    days = [
        "All"
    ] + sorted(
        timetable["Day"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_day = st.selectbox(
        "📅 Day",
        days
    )


with filter_col2:

    rooms = [
        "All"
    ] + sorted(
        timetable["Room"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_room = st.selectbox(
        "🏫 Room",
        rooms
    )


with filter_col3:

    teachers = [
        "All"
    ] + sorted(
        timetable["Teacher"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_teacher = st.selectbox(
        "👨‍🏫 Teacher",
        teachers
    )


# =========================================================
# SEARCH
# =========================================================

search_text = st.text_input(
    "🔎 Search class or subject",
    placeholder="Example: Mathematics, CSE-A, Physics..."
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_timetable = timetable.copy()


if selected_day != "All":

    filtered_timetable = filtered_timetable[
        filtered_timetable["Day"]
        .astype(str)
        .str.lower()
        == selected_day.lower()
    ]


if selected_room != "All":

    filtered_timetable = filtered_timetable[
        filtered_timetable["Room"]
        .astype(str)
        .str.lower()
        == selected_room.lower()
    ]


if selected_teacher != "All":

    filtered_timetable = filtered_timetable[
        filtered_timetable["Teacher"]
        .astype(str)
        .str.lower()
        == selected_teacher.lower()
    ]


if search_text:

    search_lower = search_text.lower()

    search_mask = (
        filtered_timetable["Class"]
        .astype(str)
        .str.lower()
        .str.contains(
            search_lower,
            na=False
        )
        |
        filtered_timetable["Subject"]
        .astype(str)
        .str.lower()
        .str.contains(
            search_lower,
            na=False
        )
    )

    filtered_timetable = filtered_timetable[
        search_mask
    ]


# =========================================================
# SORT BY TIME
# =========================================================

filtered_timetable = filtered_timetable.copy()


filtered_timetable["_sort_time"] = pd.to_datetime(
    filtered_timetable["Start"].astype(str),
    format="mixed"
)


filtered_timetable = filtered_timetable.sort_values(
    "_sort_time"
)


filtered_timetable = filtered_timetable.drop(
    columns=["_sort_time"]
)


# =========================================================
# RESULT COUNT
# =========================================================

st.caption(
    f"Showing **{len(filtered_timetable)}** "
    f"class(es)"
)


# =========================================================
# DISPLAY FILTERED TIMETABLE
# =========================================================

if filtered_timetable.empty:

    st.warning(
        "No classes match the selected filters."
    )

else:

    def highlight_status(row):

        if row["Status"] == "🔴 Room Clash":
            return [
                "background-color: #ffcccc"
                for _ in row
            ]

        if row["Status"] == "🟠 Teacher Clash":
            return [
                "background-color: #ffe0b2"
                for _ in row
            ]

        if row["Status"] == "🚫 Unavailable Room":
            return [
                "background-color: #ffb3b3"
                for _ in row
            ]

        return [
            ""
            for _ in row
        ]


    styled_timetable = filtered_timetable.style.apply(
        highlight_status,
        axis=1
    )


    st.dataframe(
        styled_timetable,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🏠 Room Clashes",
        "👨‍🏫 Teacher Clashes",
        "🚫 Unavailable Rooms",
        "📥 Reports"
    ]
)


# =========================================================
# ROOM CLASHES
# =========================================================

with tab1:

    st.subheader(
        "🏠 Room Clashes"
    )


    if not room_conflicts:

        st.success(
            "No room clashes detected."
        )


    else:

        st.error(
            f"{len(room_conflicts)} "
            "room clash(es) detected."
        )


        for index, conflict in enumerate(
            room_conflicts,
            start=1
        ):

            with st.expander(
                f"Conflict #{index} — "
                f"{conflict['day']} | "
                f"{conflict['start']} - "
                f"{conflict['end']} | "
                f"Room {conflict['room']}"
            ):

                st.write(
                    f"**Day:** {conflict['day']}"
                )

                st.write(
                    f"**Time:** "
                    f"{conflict['start']} - "
                    f"{conflict['end']}"
                )

                st.write(
                    f"**Room:** {conflict['room']}"
                )

                st.write(
                    f"**Reason:** "
                    f"{conflict['details']}"
                )


# =========================================================
# TEACHER CLASHES
# =========================================================

with tab2:

    st.subheader(
        "👨‍🏫 Teacher Clashes"
    )


    if not teacher_conflicts:

        st.success(
            "No teacher clashes detected."
        )


    else:

        st.error(
            f"{len(teacher_conflicts)} "
            "teacher clash(es) detected."
        )


        for index, conflict in enumerate(
            teacher_conflicts,
            start=1
        ):

            with st.expander(
                f"Conflict #{index} — "
                f"{conflict['day']} | "
                f"{conflict['start']} - "
                f"{conflict['end']}"
            ):

                st.write(
                    f"**Day:** {conflict['day']}"
                )

                st.write(
                    f"**Time:** "
                    f"{conflict['start']} - "
                    f"{conflict['end']}"
                )

                st.write(
                    f"**Rooms:** {conflict['room']}"
                )

                st.write(
                    f"**Reason:** "
                    f"{conflict['details']}"
                )


# =========================================================
# UNAVAILABLE ROOMS
# =========================================================

with tab3:

    st.subheader(
        "🚫 Unavailable Rooms"
    )


    if not unavailable_rooms:

        st.success(
            "No classes are assigned to unavailable rooms."
        )


    else:

        st.warning(
            f"{len(unavailable_rooms)} "
            "unavailable room assignment(s) detected."
        )


        st.write(
            "Enter the minimum room capacity required "
            "for alternative rooms."
        )


        required_capacity = st.number_input(
            "Required room capacity",
            min_value=1,
            value=50,
            step=5
        )


        for index, conflict in enumerate(
            unavailable_rooms,
            start=1
        ):

            with st.expander(
                f"Conflict #{index} — "
                f"Room {conflict['room']} | "
                f"{conflict['day']} | "
                f"{conflict['start']} - "
                f"{conflict['end']}"
            ):

                st.write(
                    f"**Room:** {conflict['room']}"
                )

                st.write(
                    f"**Day:** {conflict['day']}"
                )

                st.write(
                    f"**Time:** "
                    f"{conflict['start']} - "
                    f"{conflict['end']}"
                )

                st.write(
                    f"**Reason:** "
                    f"{conflict['details']}"
                )


                # -----------------------------------------
                # ALTERNATIVE ROOMS
                # -----------------------------------------

                suggestions = suggest_rooms(
                    required_capacity,
                    conflict["day"],
                    conflict["start"],
                    conflict["end"],
                    timetable_for_suggestions
                )


                st.markdown(
                    "#### 💡 Suggested Alternative Rooms"
                )


                if suggestions:

                    for room, capacity in suggestions:

                        st.success(
                            f"🏫 **{room}** — "
                            f"Capacity: {capacity}"
                        )


                else:

                    st.info(
                        "No suitable alternative rooms "
                        "are available for this time."
                    )


# =========================================================
# REPORTS
# =========================================================

with tab4:

    st.subheader(
        "📥 Download Reports"
    )


    # -----------------------------------------
    # CONFLICT REPORT
    # -----------------------------------------

    all_report_rows = []


    for conflict in conflicts:

        all_report_rows.append({
            "Type": conflict["type"],
            "Day": conflict["day"],
            "Start": str(conflict["start"]),
            "End": str(conflict["end"]),
            "Room": conflict["room"],
            "Details": conflict["details"]
        })


    for conflict in unavailable_rooms:

        all_report_rows.append({
            "Type": conflict["type"],
            "Day": conflict["day"],
            "Start": str(conflict["start"]),
            "End": str(conflict["end"]),
            "Room": conflict["room"],
            "Details": conflict["details"]
        })


    report_df = pd.DataFrame(
        all_report_rows
    )


    if not report_df.empty:

        report_csv = report_df.to_csv(
            index=False
        )


        st.download_button(
            label="📥 Download Conflict Report",
            data=report_csv,
            file_name="roomcheck_conflicts.csv",
            mime="text/csv"
        )


    else:

        st.info(
            "There are no conflicts to export."
        )


    # -----------------------------------------
    # CLEANED TIMETABLE
    # -----------------------------------------

    timetable_csv = timetable.to_csv(
        index=False
    )


    st.download_button(
        label="📥 Download Cleaned Timetable",
        data=timetable_csv,
        file_name="cleaned_timetable.csv",
        mime="text/csv"
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()


st.caption(
    "RoomCheck • Classroom Conflict Detection System"
)

