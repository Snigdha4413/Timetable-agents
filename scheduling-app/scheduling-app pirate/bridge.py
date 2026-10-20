"""Turns user input into a Scenario the scheduler understands."""
from scheduler import Faculty, Room, Session, Scenario, Grid, DAYS, SLOTS


class InputError(Exception):
    """Raised for bad input. The UI catches this and shows the message."""


def build_scenario(faculty_data, room_data, session_data):
    """
    faculty_data: [{"name": "Dr. Rao", "busy_days": ["Fri"]}]
    room_data:    [{"name": "R1", "capacity": 60}]
    session_data: [{"dept": "Computer Science", "faculty": "Dr. Rao",
                    "class_size": 55, "preferred_day": "Mon"}]
    """
    if not faculty_data:
        raise InputError("Add at least one faculty member.")
    if not room_data:
        raise InputError("Add at least one room.")
    if not session_data:
        raise InputError("Add at least one session.")

    # ---- rooms
    rooms = []
    for i, r in enumerate(room_data):
        if r["capacity"] <= 0:
            raise InputError(f"Room '{r['name']}' has capacity {r['capacity']}. "
                             "Capacity must be positive.")
        rooms.append(Room(rid=i + 1, name=r["name"], capacity=r["capacity"]))

    # ---- faculty: free everywhere except the days they marked busy
    faculty, fac_index = [], {}
    for i, f in enumerate(faculty_data):
        busy = set(f.get("busy_days", []))
        if len(busy) >= len(DAYS):
            raise InputError(f"{f['name']} is unavailable every day.")
        availability = {(d, s): (d not in busy) for d in DAYS for s in SLOTS}
        faculty.append(Faculty(fid=i + 1, name=f["name"],
                               availability=availability))
        fac_index[f["name"]] = i + 1

    # ---- sessions
    sessions = []
    for i, s in enumerate(session_data):
        if s["faculty"] not in fac_index:
            raise InputError(f"Session {i+1} is assigned to '{s['faculty']}', "
                             "who is not in the faculty list.")
        if s["class_size"] <= 0:
            raise InputError(f"Session {i+1} has {s['class_size']} students.")
        biggest = max(r.capacity for r in rooms)
        if s["class_size"] > biggest:
            raise InputError(
                f"Session {i+1} has {s['class_size']} students but the largest "
                f"room holds {biggest}. Add a bigger room.")
        sessions.append(Session(sid=i + 1, dept=s["dept"],
                                faculty_id=fac_index[s["faculty"]],
                                class_size=s["class_size"],
                                preferred_day=s.get("preferred_day")))

    sc = Scenario(sessions=sessions, faculty=faculty, rooms=rooms)
    check_feasible(sc)
    return sc


def check_feasible(sc):
    """Catch impossible setups BEFORE running, so the user gets a clear
    message instead of a half-filled timetable."""
    cells = len(DAYS) * len(SLOTS) * len(sc.rooms)
    n_depts = len({s.dept for s in sc.sessions})
    dept_cap = n_depts * len(DAYS) * len(SLOTS)   # a dept cannot be in two places
    ceiling = min(cells, dept_cap)

    if len(sc.sessions) > ceiling:
        raise InputError(
            f"{len(sc.sessions)} sessions, but this setup holds at most "
            f"{ceiling} ({len(sc.rooms)} rooms x {len(DAYS)} days x "
            f"{len(SLOTS)} periods, limited by the one-class-per-department-"
            f"per-period rule). Add rooms or remove sessions.")

    grid = Grid(sc)
    for s in sc.sessions:
        if not grid.legal_cells(s):
            raise InputError(
                f"Session {s.sid} ({s.dept}, {s.class_size} students) has no "
                "possible slot. Its faculty may be too busy, or no room fits.")


def warnings_for(sc, trained_sessions=60):
    """Non-blocking notes to show the user."""
    out = []
    if len(sc.sessions) > trained_sessions * 1.5:
        out.append(
            f"Agents were trained on {trained_sessions} sessions. You entered "
            f"{len(sc.sessions)}, so results may be worse than our reported "
            "numbers.")
    load = len(sc.sessions) / (len(DAYS) * len(SLOTS) * len(sc.rooms))
    if load > 0.8:
        out.append(f"Grid is {load:.0%} full. Tight timetables mean more "
                   "clashes and lower preference scores.")
    return out


def parse_sessions_csv(df):
    """Clean an uploaded sessions table.
    Returns (rows, notes): rows are ready-to-use session dicts, notes are
    plain-language messages about anything skipped or fixed."""
    from scheduler import DAYS
    notes = []
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = [c for c in ("dept", "faculty", "class_size") if c not in df.columns]
    if missing:
        raise InputError("The CSV is missing column(s): " + ", ".join(missing) +
                         ". Expected: dept, faculty, class_size, preferred_day.")
    if "preferred_day" not in df.columns:
        df["preferred_day"] = None
        notes.append("No preferred_day column found, so no day preferences were set.")
    rows, skipped, bad_days = [], 0, 0
    for _, r in df.iterrows():
        try:
            size = int(float(r["class_size"]))
        except (TypeError, ValueError):
            size = 0
        dept, fac = str(r["dept"]).strip(), str(r["faculty"]).strip()
        if size <= 0 or dept in ("", "nan") or fac in ("", "nan"):
            skipped += 1
            continue
        day = str(r["preferred_day"]).strip()[:3].title() if r["preferred_day"] == r["preferred_day"] else ""
        if day not in DAYS:
            bad_days += day not in ("", "Nan", "Non")
            day = None
        rows.append({"dept": dept, "faculty": fac, "class_size": size,
                     "preferred_day": day})
    if skipped:
        notes.append(f"{skipped} row(s) skipped: missing department, faculty or a valid class size.")
    if bad_days:
        notes.append(f"{bad_days} row(s) had an unrecognised day and were set to no preference.")
    return rows, notes
