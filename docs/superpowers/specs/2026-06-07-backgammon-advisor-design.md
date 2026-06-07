# Backgammon Advisor — Design Spec
_Date: 2026-06-07_

## Overview

A web-based backgammon advisor. The user inputs their dice roll each turn; the app recommends the best move, shows a histogram of all possible dice outcomes, displays win/gammon probabilities, and advises on the doubling cube. No AI API — pure probability and heuristic evaluation.

---

## Core Features

1. **Move advisor** — given the current board + dice rolled, find the best legal move using one-ply lookahead.
2. **Dice outcome histogram** — for the current position, score all 21 unique dice combinations and render as a bar chart.
3. **Position analysis** — show Win%, Gammon%, Backgammon% for the current player, computed via heuristic evaluation.
4. **Doubling cube advice** — based on win probability, advise whether to double and whether to accept a double.
5. **Game plan modes** — three evaluation profiles that adjust the weight of aggressive vs. safe heuristics:
   - **Bold** — prioritizes hitting, priming attacks, gammon wins
   - **Wise** — balanced; the default
   - **Caution** — prioritizes safety, avoids blots, prefers racing
6. **Override move** — the user can ignore the advice and enter the move they actually played; the board updates correctly regardless.
7. **Move history log** — full record of every move (yours + opponent) shown below the board.

---

## Architecture

### Stack
- **Backend**: Python 3.11+, Flask
- **Frontend**: Single HTML page + vanilla JS (no framework), served by Flask
- **State**: Server-side, stored in Flask session (cookie-backed)
- **Deployment**: `python app.py` locally; GitHub repo for version control

### File Structure

```
backgammon-advisor/
├── app.py                  # Flask app, routes, session management
├── backgammon/
│   ├── board.py            # Board state, move application, legal move generation
│   ├── evaluator.py        # Position scoring heuristics
│   └── advisor.py          # One-ply lookahead, histogram, cube advice
├── templates/
│   └── index.html          # Single-page UI
├── static/
│   ├── style.css
│   └── app.js
├── CLAUDE.md
├── requirements.txt
└── docs/
    └── superpowers/specs/
        └── 2026-06-07-backgammon-advisor-design.md
```

---

## Board Representation

- Array of 26 integers: indices 0–25
  - Index 0 = White's bar
  - Index 25 = Red's bar
  - Indices 1–24 = points 1–24
- Positive value = Red checkers (user); negative = White checkers (opponent)
- Off-board pieces tracked separately per player
- Opening position is hardcoded as the standard backgammon start

---

## Game Flow (per turn)

```
User's turn:
  1. User enters dice (e.g. "5 3")
  2. Backend generates all legal moves
  3. One-ply lookahead scores each move
  4. Returns: best move, all-outcomes histogram, Win%, Gammon%, cube advice
  5. User clicks "Take Advice" OR enters override move
  6. Board updates

Opponent's turn:
  1. User enters opponent dice + move notation (e.g. "4 2" / "24/20 13/11")
  2. Board updates, next turn begins
```

---

## Move Generation

- Generate all legal checklists for a given dice roll, respecting:
  - Must use both dice if possible
  - Higher die must be used if only one can be played
  - Doubles = four moves with same value
- Represent moves as list of (from_point, to_point) pairs
- Handle: hitting blots (sending to bar), bearing off, entering from bar

---

## Position Evaluator (heuristics)

Returns a score in range [-1, +1] from Red's perspective. Weights shift by game plan mode.

| Factor | Bold | Wise | Caution |
|---|---|---|---|
| Pip count advantage | 0.3 | 0.4 | 0.5 |
| Blot count (penalty) | 0.1 | 0.2 | 0.4 |
| Prime strength (consecutive points made) | 0.3 | 0.2 | 0.1 |
| Home board strength | 0.2 | 0.2 | 0.2 |
| Hit threat (opponent blots reachable) | 0.1 | 0.0 | -0.1 |

Win%, Gammon%, Backgammon% are derived from the score via a simple sigmoid mapping calibrated to known backgammon equity tables.

---

## One-Ply Lookahead

For each legal move M:
1. Apply M → get new board state B'
2. For each of the 21 unique opponent dice combos (weighted by probability):
   a. Find opponent's best response on B'
   b. Evaluate resulting position from opponent's POV
3. Score(M) = eval(B') − weighted_avg(opponent_best_response_evals)

Return the M with the highest Score.

---

## Dice Outcome Histogram

- Enumerate all 21 unique dice combos (11, 12, 13, ... 66) with frequencies (doubles = 1/36, others = 2/36)
- For each combo, find best move and its Score
- Return sorted list for rendering as color-coded bar chart (green = positive, red = negative)

---

## Doubling Cube Advice

Based on Win% (W):
- **Double**: W ≥ 70% (strong enough to double, opponent may still accept)
- **Double urgently**: W ≥ 85% (opponent should drop)
- **Accept**: W (as receiver) ≥ 25% (basic take/pass threshold)
- **Pass**: W < 25%
- **No action**: 40% ≤ W < 70%

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Serve the UI |
| GET | `/api/state` | Return full board state + analysis |
| POST | `/api/new-game` | Reset to opening position |
| POST | `/api/advise` | `{dice: [5,3], plan: "wise"}` → returns best move, histogram, analysis |
| POST | `/api/apply-move` | `{move: "13/8 8/5"}` → update board with your move |
| POST | `/api/opponent-move` | `{dice: [4,2], move: "24/20 13/11"}` → update board |

---

## Frontend

- Single `index.html` loaded once; JS calls the API and re-renders sections
- Board rendered as SVG or HTML grid with triangular points and colored checkers
- Game plan tabs switch the active mode (sent with every `/api/advise` call)
- Histogram rendered as horizontal bar chart in pure CSS/JS
- No page reloads — all updates via `fetch()` + DOM manipulation

---

## CLAUDE.md

A `CLAUDE.md` file will be created at project root documenting:
- Project purpose and structure
- How to run locally
- Backgammon notation conventions used in the codebase
- Heuristic weight tables and how to tune them

---

## Out of Scope

- User accounts / persistence across browser sessions
- Multiplayer
- AI/LLM-based evaluation
- Mobile app
- Actual rollout statistics from a database
