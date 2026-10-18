import json
from datetime import datetime

import pandas as pd
import streamlit as st

from bridge import build_scenario, warnings_for, parse_sessions_csv, InputError
from runner import run_schedule, timetable_rows, DEFAULT_METHOD, TRAINED_SESSIONS
from presets import PRESETS
from theme import inject_theme, hero
from scheduler import DAYS, SLOTS

st.set_page_config(page_title="Course Scheduling Agents", page_icon="🛵", layout="wide")
inject_theme()
st.title("Multi-Agent Course Scheduling")
st.caption("Department and room agents negotiate a conflict-free timetable")
hero()

# ---------- session state ----------
for key in ["faculty", "rooms", "sessions", "log"]:
    st.session_state.setdefault(key, [])
st.session_state.setdefault("uploader_n", 0)
S = st.session_state


def log(msg):
    S.log.insert(0, f"{datetime.now():%H:%M}  {msg}")
    del S.log[8:]


def done(msg):
    """Record a change, show a toast after the rerun, and refresh the page."""
    log(msg)
    S.flash = msg
    st.rerun()


if S.get("flash"):
    st.toast(S.pop("flash"))

fac_names = [f["name"] for f in S.faculty]
max_cap = max((r["capacity"] for r in S.rooms), default=0)

# ---------- sidebar ----------
with st.sidebar:
    st.header("Start from a preset")
    choice = st.selectbox("Preset", list(PRESETS))
    if st.button("Load preset (replaces everything)"):
        f, r, s = PRESETS[choice]()
        S.faculty, S.rooms = f, r
        S.sessions = [{**x, "source": "preset"} for x in s]
        done(f"Loaded preset '{choice}': {len(f)} faculty, {len(r)} rooms, {len(s)} sessions")
    if st.button("Clear everything"):
        S.faculty, S.rooms, S.sessions = [], [], []
        done("Cleared all faculty, rooms and sessions")

    st.divider()
    st.header("Method")
    method = st.radio(
        "Scheduling method", ["q_learning", "expected_sarsa", "greedy"],
        index=["q_learning", "expected_sarsa", "greedy"].index(DEFAULT_METHOD),
        format_func=lambda m: {"q_learning": "Q-Learning (recommended)",
                               "expected_sarsa": "Expected SARSA",
                               "greedy": "Greedy (no learning)"}[m])

    st.divider()
    st.header("Recent changes")
    if S.log:
        for line in S.log:
            st.caption(line)
    else:
        st.caption("Nothing yet. Add or upload something.")

# ---------- live summary of everything entered ----------
n_cells = 30 * len(S.rooms)
src_counts = pd.Series([s.get("source", "preset") for s in S.sessions]).value_counts()
m1, m2, m3, m4 = st.columns(4)
m1.metric("Faculty", len(S.faculty))
m2.metric("Rooms", len(S.rooms))
m3.metric("Sessions", len(S.sessions))
m4.metric("Grid load", f"{len(S.sessions) / n_cells:.0%}" if n_cells else "n/a")
if len(S.sessions):
    label = {"manual": "added by hand", "csv": "from CSV", "preset": "from preset"}
    st.caption("Sessions: " + " · ".join(f"{n} {label.get(k, k)}" for k, n in src_counts.items()))

# ---------- input tabs ----------
tab_f, tab_r, tab_s = st.tabs(["Faculty", "Rooms", "Sessions"])

with tab_f:
    with st.form("add_faculty", clear_on_submit=True):
        c1, c2 = st.columns([2, 3])
        name = c1.text_input("Name")
        busy = c2.multiselect("Unavailable days", DAYS)
        if st.form_submit_button("Add faculty"):
            if not name.strip():
                st.error("Enter a name.")
            elif name.strip() in fac_names:
                st.error(f"'{name.strip()}' is already in the list.")
            else:
                S.faculty.append({"name": name.strip(), "busy_days": busy})
                done(f"Added faculty {name.strip()}")
    if S.faculty:
        st.dataframe(pd.DataFrame([{"Name": f["name"],
                                    "Unavailable days": ", ".join(f.get("busy_days", [])) or "none"}
                                   for f in S.faculty], index=range(1, len(S.faculty) + 1)),
                     width="stretch", height=min(400, 40 + 35 * len(S.faculty)))
        gone = st.multiselect("Remove faculty", fac_names, key="rm_fac")
        if gone and st.button("Remove selected faculty"):
            S.faculty = [f for f in S.faculty if f["name"] not in gone]
            done(f"Removed {len(gone)} faculty. Sessions that use them must be removed too.")
    else:
        st.info("No faculty yet.")

with tab_r:
    with st.form("add_room", clear_on_submit=True):
        c1, c2 = st.columns(2)
        rname = c1.text_input("Room name")
        cap = c2.number_input("Capacity", min_value=1, value=60)
        if st.form_submit_button("Add room"):
            if not rname.strip():
                st.error("Enter a room name.")
            elif rname.strip() in [r["name"] for r in S.rooms]:
                st.error(f"'{rname.strip()}' is already in the list.")
            else:
                S.rooms.append({"name": rname.strip(), "capacity": int(cap)})
                done(f"Added room {rname.strip()} (capacity {int(cap)})")
    if S.rooms:
        st.dataframe(pd.DataFrame(S.rooms, index=range(1, len(S.rooms) + 1)), width="stretch")
        gone = st.multiselect("Remove rooms", [r["name"] for r in S.rooms], key="rm_room")
        if gone and st.button("Remove selected rooms"):
            S.rooms = [r for r in S.rooms if r["name"] not in gone]
            done(f"Removed {len(gone)} room(s)")
    else:
        st.info("No rooms yet.")

with tab_s:
    left, right = st.columns(2)

    # ---- add by hand
    with left:
        st.subheader("Add by hand")
        if not S.faculty:
            st.info("Add a faculty member first (Faculty tab) or load a preset.")
        else:
            known = sorted({s["dept"] for s in S.sessions})
            with st.form("add_session", clear_on_submit=True):
                dept = st.text_input("Department",
                                     help="Existing: " + (", ".join(known) or "none yet"))
                c1, c2 = st.columns(2)
                fac = c1.selectbox("Faculty", fac_names)
                size = c2.number_input("Students", min_value=1, value=50)
                c3, c4 = st.columns(2)
                pday = c3.selectbox("Preferred day", ["(none)"] + DAYS)
                copies = c4.number_input("How many sessions", min_value=1, max_value=30, value=1)
                if st.form_submit_button("Add session(s)"):
                    if not dept.strip():
                        st.error("Enter a department.")
                    elif max_cap and size > max_cap:
                        st.error(f"{int(size)} students is more than the largest room ({max_cap}).")
                    else:
                        row = {"dept": dept.strip(), "faculty": fac, "class_size": int(size),
                               "preferred_day": None if pday == "(none)" else pday,
                               "source": "manual"}
                        S.sessions.extend(dict(row) for _ in range(int(copies)))
                        done(f"Added {int(copies)} session(s) by hand: {dept.strip()}, {fac}")

    # ---- import CSV
    with right:
        st.subheader("Import CSV")
        mode = st.radio("When importing", ["Add to existing sessions", "Replace all sessions"],
                        horizontal=True)
        up = st.file_uploader("Sessions CSV (dept, faculty, class_size, preferred_day)",
                              type="csv", key=f"csv_{S.uploader_n}")
        if up is not None:
            try:
                rows, notes = parse_sessions_csv(pd.read_csv(up))
            except InputError as e:
                st.error(str(e))
                rows = []
            except Exception:
                st.error("Could not read that file as a CSV.")
                rows = []
            for n in notes:
                st.warning(n)
            if rows:
                missing = sorted({r["faculty"] for r in rows} - set(fac_names))
                if missing:
                    st.warning("Not in the Faculty list yet: " + ", ".join(missing) +
                               ". Add them before generating.")
                st.caption(f"{len(rows)} valid session(s) found. Preview:")
                st.dataframe(pd.DataFrame(rows).head(5), width="stretch", hide_index=True)
                if st.button(f"Import {len(rows)} sessions"):
                    tagged = [{**r, "source": "csv"} for r in rows]
                    S.sessions = tagged if mode.startswith("Replace") else S.sessions + tagged
                    S.uploader_n += 1
                    done(f"Imported {len(rows)} sessions from {up.name} "
                         f"({'replaced' if mode.startswith('Replace') else 'added'})")

    # ---- everything entered so far
    st.divider()
    st.subheader(f"All sessions ({len(S.sessions)})")
    if S.sessions:
        sdf = pd.DataFrame(S.sessions)
        sdf["source"] = sdf.get("source", "preset")
        sdf["source"] = sdf["source"].fillna("preset")
        sdf = sdf[["dept", "faculty", "class_size", "preferred_day", "source"]]
        sdf.index = range(1, len(sdf) + 1)
        tint = {"manual": "background-color: #BFE6F4",
                "csv": "background-color: #F7C6DE"}
        st.dataframe(sdf.style.apply(lambda r: [tint.get(r["source"], "")] * len(r), axis=1),
                     width="stretch", height=min(480, 40 + 35 * len(sdf)))
        st.caption("Blue rows were added by hand, pink rows came from a CSV.")
        c1, c2 = st.columns([3, 1])
        gone = c1.multiselect("Remove sessions by number", list(sdf.index), key="rm_sess")
        if gone and c1.button("Remove selected sessions"):
            S.sessions = [s for i, s in enumerate(S.sessions, 1) if i not in gone]
            done(f"Removed {len(gone)} session(s)")
        if c2.button("Clear all sessions"):
            S.sessions = []
            done("Cleared all sessions")
    else:
        st.info("No sessions yet. Add one by hand or import a CSV.")

# ---------- generate ----------
st.divider()
sig = json.dumps([S.faculty, S.rooms, S.sessions], sort_keys=True, default=str)
st.write(f"Ready to schedule **{len(S.sessions)}** sessions using **{len(S.faculty)}** faculty "
         f"and **{len(S.rooms)}** rooms.")
if st.button("Generate timetable", type="primary"):
    S.result = None
    try:
        sc = build_scenario(S.faculty, S.rooms, S.sessions)
        with st.spinner("Agents negotiating..."):
            grid, m = run_schedule(sc, method)
        S.result = {"sc": sc, "m": m, "df": pd.DataFrame(timetable_rows(sc, grid)),
                    "method": method, "sig": sig}
        if m["violations"] == 0:
            st.balloons()
    except InputError as e:
        st.error(str(e))

res = S.get("result")
if res:
    sc, m, df = res["sc"], res["m"], res["df"]
    if res["sig"] != sig:
        st.warning("You changed the inputs after this timetable was generated. "
                   "Click Generate timetable to update it.")
    for w in warnings_for(sc, TRAINED_SESSIONS):
        st.warning(w)
    st.caption(f"Method used: {res['method']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Placed", f"{m['placed']}/{len(sc.sessions)}")
    c2.metric("Avg preference", f"{m['preference']:.2f} / 7")
    c3.metric("Worst-off dept", f"{m['fairness_min']:.2f}")
    c4.metric("Rule violations", int(m["violations"]))

    if m["violations"] == 0:
        st.success("Every constraint satisfied: no double-booked rooms, "
                   "faculty or student groups.")
    else:
        st.error("Constraint violations found — this is a bug, please report.")

    view = st.radio("View by", ["Room", "Department", "Full list"], horizontal=True)
    if view == "Full list":
        st.dataframe(df, width="stretch", height=420)
    else:
        col = "Room" if view == "Room" else "Department"
        for key in sorted(df[col].unique()):
            st.subheader(key)
            sub = df[df[col] == key]
            table = pd.DataFrame("", index=[f"P{p}" for p in SLOTS], columns=DAYS)
            for _, r in sub.iterrows():
                label = f"{r['Department'][:12]}" if view == "Room" else r["Room"]
                table.loc[f"P{r['Period']}", r["Day"]] = label
            st.dataframe(table, width="stretch")

    st.download_button("Download timetable CSV", df.to_csv(index=False),
                       "timetable.csv", "text/csv")

    if st.checkbox("Compare all three methods"):
        results = []
        for mth in ["greedy", "expected_sarsa", "q_learning"]:
            _, mm = run_schedule(sc, mth)
            results.append({
                "Method": {"greedy": "Greedy", "expected_sarsa": "Expected SARSA",
                           "q_learning": "Q-Learning"}[mth],
                "Placed": f"{mm['placed']}/{len(sc.sessions)}",
                "Avg preference": round(mm["preference"], 2),
                "Worst-off dept": round(mm["fairness_min"], 2),
                "Clashes": mm["clashes"],
                "Rounds": mm["rounds"],
                "Violations": int(mm["violations"]),
            })
        st.dataframe(pd.DataFrame(results), width="stretch")
        st.caption(
            "Greedy takes the best-liked free slot every time, so it scores "
            "higher on preference. The learning agents clash far less, because "
            "they learn when to concede. Across 5 seeds at 75% grid load: "
            "greedy 28.2 clashes, Q-Learning 18.9.")
