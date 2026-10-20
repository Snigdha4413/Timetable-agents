"""Ready-made scenarios for the demo."""
import random

DEPTS = ["Computer Science", "Data Science", "Civil",
         "Mathematics & Science", "Artificial Intelligence", "Mechanical"]
DAY_LIST = ["Mon", "Tue", "Wed", "Thu", "Fri"]


def _make(n_sessions, n_rooms, n_faculty, seed=0):
    rng = random.Random(seed)
    faculty = [{"name": f"Prof {i+1}",
                "busy_days": rng.sample(DAY_LIST, rng.choice([0, 1]))}
               for i in range(n_faculty)]
    caps = [50, 70, 110, 140]
    rooms = [{"name": f"R{i+1}", "capacity": caps[i % 4]} for i in range(n_rooms)]
    sessions = [{"dept": DEPTS[i % len(DEPTS)],
                 "faculty": faculty[i % n_faculty]["name"],
                 "class_size": rng.choice([30, 40, 50, 60]),
                 "preferred_day": rng.choice(DAY_LIST)}
                for i in range(n_sessions)]
    return faculty, rooms, sessions


PRESETS = {
    "Small (10 sessions)":            lambda: _make(10, 2, 4),
    "Trained scale (60 sessions)":    lambda: _make(60, 4, 24),
    "Overloaded (110 sessions)":      lambda: _make(110, 4, 36),
}
