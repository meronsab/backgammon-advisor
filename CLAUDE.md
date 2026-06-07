# Backgammon Advisor

Do not use any superpowers skills unless explicitly asked.

Flask web app that advises the best move in backgammon using one-ply lookahead and heuristic evaluation.

## Running locally

```bash
python3 -m pip install flask pytest --user --break-system-packages
python3 app.py        # visit http://localhost:5000
python3 -m pytest     # run all tests
```

## Project layout

- `backgammon/board.py` — Board dataclass, move generation, move application
- `backgammon/evaluator.py` — Position heuristics and win probability
- `backgammon/advisor.py` — One-ply lookahead, histogram generation
- `app.py` — Flask routes and session management
- `templates/index.html` + `static/` — Single-page frontend

## Board convention

Red (you) moves from point 24 → 1. White (opponent) moves 1 → 24.
`board.points[i]` > 0 = Red, < 0 = White. Red home board = points 1–6.
Move notation: `"13/8 8/5"`. Bar entry: `"bar/19"`. Bear off: `"3/off"`.

## Heuristic weights (evaluator.py)

Three game plan modes shift weights: `PLAN_WEIGHTS` dict in `evaluator.py`.
Tune values there to change advisor aggressiveness.
