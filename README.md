# Backgammon Advisor

A web-based backgammon advisor that recommends the best move for your position using one-ply lookahead and heuristic evaluation.

## Features

- **Move advisor** — enter your dice roll and get the best move recommendation
- **3 game plans** — Bold (aggressive), Wise (balanced), Caution (safe)
- **Dice outcome histogram** — see all 21 possible rolls scored and ranked
- **Position analysis** — Win%, Gammon%, Backgammon% for your current position
- **Doubling cube advice** — whether to double and whether to accept
- **Override** — ignore the advice and enter the move you actually played
- **Move history** — full log of every move tracked during the game

## Running locally

```bash
git clone https://github.com/YOUR_USERNAME/backgammon-advisor.git
cd backgammon-advisor
python3 -m pip install -r requirements.txt --user --break-system-packages
python3 app.py
```

Open http://localhost:5000 in your browser.

## How to use

1. Click **New Game** to start from the opening position
2. Roll your dice physically, then enter the two values and click **Get Advice**
3. The advisor shows the best move, your win probability, and a histogram of all outcomes
4. Click **Take Advice** to apply the move, or **Override** to enter your actual move
5. Enter your opponent's dice and move, click **Apply & Next Turn**
6. Repeat each turn

## Board convention

- You (Red) move from point 24 → 1
- Opponent (White) moves from point 1 → 24
- Move notation: `13/8 8/5` (from/to), `bar/19` (bar entry), `3/off` (bear off)

## Running tests

```bash
python3 -m pytest
```

## License

MIT
