from backgammon.board import opening_board, Board
from backgammon.evaluator import evaluate, PLAN_WEIGHTS, win_probability, cube_advice

def test_evaluate_opening_near_zero():
    b = opening_board()
    score = evaluate(b, 'wise')
    assert -0.1 < score < 0.1

def test_evaluate_returns_float():
    b = opening_board()
    assert isinstance(evaluate(b, 'wise'), float)

def test_evaluate_red_ahead_positive():
    b = Board(points=[0]*25)
    b.points[3] = 5; b.points[4] = 5; b.points[5] = 5
    b.points[20] = -15
    assert evaluate(b, 'wise') > 0.1

def test_evaluate_white_ahead_negative():
    b = Board(points=[0]*25)
    b.points[22] = -5; b.points[21] = -5; b.points[20] = -5
    b.points[5] = 15
    assert evaluate(b, 'wise') < -0.1

def test_plan_weights_keys():
    assert set(PLAN_WEIGHTS.keys()) == {'bold', 'wise', 'caution'}
    for plan in PLAN_WEIGHTS.values():
        for k in ('pip', 'blot', 'prime', 'home', 'hit'):
            assert k in plan

def test_win_probability_symmetric():
    probs = win_probability(0.0)
    assert 0.48 < probs['win'] < 0.52

def test_win_probability_strong_red():
    probs = win_probability(0.8)
    assert probs['win'] > 0.85
    assert probs['gammon'] > 0.15
    assert probs['backgammon'] >= 0.0

def test_win_probability_keys():
    assert set(win_probability(0.0).keys()) == {'win', 'gammon', 'backgammon'}

def test_cube_advice_double():
    assert cube_advice(0.73)['action'] == 'double'

def test_cube_advice_hold():
    assert cube_advice(0.55)['action'] == 'hold'

def test_cube_advice_accept():
    assert cube_advice(0.70)['opponent_should'] == 'accept'

def test_cube_advice_pass():
    assert cube_advice(0.87)['opponent_should'] == 'pass'
