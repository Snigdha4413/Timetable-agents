import pytest
from bridge import build_scenario, InputError
from runner import run_schedule
from presets import PRESETS


def test_presets_all_valid():
    for name, make in PRESETS.items():
        f, r, s = make()
        sc = build_scenario(f, r, s)
        for method in ["greedy", "expected_sarsa", "q_learning"]:
            grid, m = run_schedule(sc, method)
            assert m["violations"] == 0, f"{name} / {method} broke a rule"


def test_rejects_unknown_faculty():
    with pytest.raises(InputError):
        build_scenario([{"name": "A", "busy_days": []}],
                       [{"name": "R1", "capacity": 60}],
                       [{"dept": "CS", "faculty": "Nobody", "class_size": 30}])


def test_rejects_class_bigger_than_every_room():
    with pytest.raises(InputError):
        build_scenario([{"name": "A", "busy_days": []}],
                       [{"name": "R1", "capacity": 30}],
                       [{"dept": "CS", "faculty": "A", "class_size": 500}])


def test_rejects_impossible_load():
    f = [{"name": "A", "busy_days": []}]
    r = [{"name": "R1", "capacity": 60}]
    s = [{"dept": "CS", "faculty": "A", "class_size": 30}] * 500
    with pytest.raises(InputError):
        build_scenario(f, r, s)


def test_unknown_department_falls_back():
    """A department name the agents never trained on must not crash."""
    f = [{"name": "A", "busy_days": []}]
    r = [{"name": "R1", "capacity": 60}]
    s = [{"dept": "Electronics", "faculty": "A", "class_size": 30}]
    sc = build_scenario(f, r, s)
    grid, m = run_schedule(sc, "q_learning")
    assert m["violations"] == 0


def test_csv_parser_cleans_rows():
    import pandas as pd
    from bridge import parse_sessions_csv
    df = pd.DataFrame({"Dept": ["CS", "", "CS"], "Faculty": ["A", "A", "A"],
                       "class_size": [30, 40, "x"], "preferred_day": ["mon", "Tue", "Fri"]})
    rows, notes = parse_sessions_csv(df)
    assert len(rows) == 1 and rows[0]["preferred_day"] == "Mon" and notes
    with pytest.raises(InputError):
        parse_sessions_csv(pd.DataFrame({"dept": ["CS"]}))
