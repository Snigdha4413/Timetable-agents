"""Loads pre-trained agents and produces a timetable."""
import pickle
from collections import defaultdict
import numpy as np

from scheduler import (Grid, DAYS, SLOTS, validate, run_episode, run_baseline,
                       make_dept_agents, make_room_agents, ACTION_NAMES,
                       RoomAgent)

with open("trained_agents.pkl", "rb") as f:
    BLOB = pickle.load(f)

DEFAULT_METHOD = BLOB.get("default_method", "q_learning")
TRAINED_SESSIONS = BLOB.get("trained_sessions", 60)


def _restore(agent, stored_Q, n_actions):
    """Put a saved Q-table back into a fresh agent.

    The pickle holds plain dicts because lambdas cannot be pickled. We wrap
    it in a defaultdict so a state the agent never saw in training returns
    zeros instead of raising KeyError -- which WILL happen on user input.
    """
    agent.Q = defaultdict(lambda: np.zeros(n_actions), stored_Q)
    agent.eps = 0.02
    return agent


def _load_agents(sc, method):
    """Rebuild agents for THIS scenario using the saved tables.

    Departments are keyed by name and rooms by id. A user's "Electronics"
    department or 5th room has no trained table, so we fall back to any
    trained one -- the six departments converge on similar policies.
    """
    saved = BLOB[method]
    dept_agents = make_dept_agents(sc)
    room_agents = make_room_agents(sc)

    saved_dept = list(saved["dept"].values())
    for name, ag in dept_agents.items():
        entry = saved["dept"].get(name, saved_dept[0])      # fallback
        _restore(ag, entry["Q"], len(ACTION_NAMES))

    saved_rooms = list(saved["rooms"].values())
    for rid, ag in room_agents.items():
        entry = saved["rooms"].get(rid, saved_rooms[0])     # fallback
        _restore(ag, entry["Q"], len(RoomAgent.RULES))

    return dept_agents, room_agents


def run_schedule(sc, method="q_learning"):
    """method: "greedy" | "expected_sarsa" | "q_learning"
    Returns (grid, metrics_dict)."""
    grid = Grid(sc)

    if method == "greedy":
        m = run_baseline(sc, "greedy_pref")
        # run_baseline builds its own grid, so re-run to keep ours
        grid = Grid(sc)
        m = run_baseline_into(sc, grid)
    else:
        dept_agents, room_agents = _load_agents(sc, method)
        m = run_episode(sc, grid, dept_agents, room_agents, learn=False)

    return grid, m


def run_baseline_into(sc, grid):
    """Greedy, writing into the grid we hand it, so the UI can show it."""
    from scheduler import RoundView, Bid, resolve_round, metrics
    room_agents = make_room_agents(sc)
    for a in room_agents.values():
        a.eps = 0.0
    clashes = offers = accepted = 0

    for rnd in range(120):
        view = RoundView(grid)
        bids = []
        for d in sorted({s.dept for s in sc.sessions}):
            mine = [s for s in sc.sessions_for_dept(d)
                    if s.sid in view.options and view.options[s.sid]]
            if not mine:
                continue
            best = None
            for x in mine:
                for c in view.options[x.sid]:
                    v = x.pref(c[0], c[1])
                    if best is None or v > best[2]:
                        best = (x, c, v)
            s, c, _ = best
            bids.append(Bid(d, s, c[0], c[1], c[2], len(view.options[s.sid])))
        if not bids:
            break
        out = resolve_round(bids, room_agents, grid)
        offers += len(bids)
        accepted += len(out["placed"])
        clashes += len(out["rejected"])
        if len(grid.placed) == len(sc.sessions):
            break
    return metrics(sc, grid, rnd + 1, {}, {}, clashes, offers, accepted)


def timetable_rows(sc, grid):
    """Flat list of placements -- easy to turn into a DataFrame."""
    by_id = {s.sid: s for s in sc.sessions}
    rows = []
    for sid, (day, slot, rid) in grid.placed.items():
        s = by_id[sid]
        room = next(r for r in sc.rooms if r.rid == rid)
        fac = sc.faculty_by_id(s.faculty_id)
        rows.append({"Session": sid, "Department": s.dept, "Faculty": fac.name,
                     "Students": s.class_size, "Day": day, "Period": slot,
                     "Room": room.name,
                     "Preference": round(s.pref(day, slot), 2)})
    return sorted(rows, key=lambda r: (DAYS.index(r["Day"]), r["Period"]))
