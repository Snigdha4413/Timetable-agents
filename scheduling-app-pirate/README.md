# Multi-Agent Course Scheduling

Live demo: <your streamlit link>

Department and room agents learn to negotiate a university timetable using
reinforcement learning. Every timetable produced satisfies all hard
constraints: no double-booked rooms, faculty or student groups.

## How it works
6 department agents propose slots for their classes; 4 room agents decide
who gets contested slots. Both learn with Expected SARSA (and Q-Learning
as a comparison). Agents are only shown legal slots, so invalid timetables
cannot be produced.

## What we found
Across 5 random seeds at 75% grid load:

| method | preference | fairness | clashes |
|---|---|---|---|
| Expected SARSA | 5.62 ±0.12 | 5.14 ±0.07 | 22.6 ±4.8 |
| Q-Learning | 5.78 ±0.09 | 5.33 ±0.30 | 18.9 ±2.8 |
| Greedy | 5.95 ±0.05 | 5.68 ±0.09 | 28.2 ±5.0 |

A greedy heuristic still produces better-liked slots than either learner.
The learning agents' advantage is that they clash far less — they learn
when to concede. We also predicted that on-policy learning (Expected
SARSA) would beat off-policy (Q-Learning) under competing agents; across
5 seeds it did not.

## Limitations
- Agents trained at one scale (60 sessions); larger inputs degrade.
- Training used random faculty availability; real timetables block in
  patterns, and this is untested on real institutional data.
- Tabular Q-tables will not scale to a full university.
