from backgammon.board import (
    Board, opening_board, pip_count, parse_move,
    apply_move, generate_moves, all_home,
)

def test_opening_board_red_pip_count():
    b = opening_board()
    assert pip_count(b, 'red') == 167

def test_opening_board_white_pip_count():
    b = opening_board()
    assert pip_count(b, 'white') == 167

def test_opening_board_red_checkers():
    b = opening_board()
    assert b.points[24] == 2
    assert b.points[13] == 5
    assert b.points[8] == 3
    assert b.points[6] == 5

def test_opening_board_white_checkers():
    b = opening_board()
    assert b.points[1] == -2
    assert b.points[12] == -5
    assert b.points[17] == -3
    assert b.points[19] == -5

def test_opening_board_no_bar():
    b = opening_board()
    assert b.red_bar == 0
    assert b.white_bar == 0

def test_parse_move_normal():
    assert parse_move("13/8 8/5") == [(13, 8), (8, 5)]

def test_parse_move_bar_entry():
    assert parse_move("bar/19") == [(0, 19)]

def test_parse_move_bear_off():
    assert parse_move("3/off") == [(3, 0)]

def test_parse_move_single():
    assert parse_move("24/18") == [(24, 18)]

# ── Move application ──

def test_apply_normal_move_red():
    b = opening_board()
    new_b = apply_move(b, [(13, 8)], 'red')
    assert new_b.points[13] == 4
    assert new_b.points[8] == 4
    assert b.points[13] == 5  # original unchanged

def test_apply_move_hits_white_blot():
    b = opening_board()
    b.points[10] = -1
    new_b = apply_move(b, [(13, 10)], 'red')
    assert new_b.points[10] == 1
    assert new_b.white_bar == 1

def test_apply_bear_off_red():
    b = Board(points=[0]*25)
    b.points[3] = 2
    new_b = apply_move(b, [(3, 0)], 'red')
    assert new_b.points[3] == 1
    assert new_b.red_off == 1

def test_apply_bar_entry_red():
    b = Board(points=[0]*25)
    b.red_bar = 1
    new_b = apply_move(b, [(0, 22)], 'red')
    assert new_b.red_bar == 0
    assert new_b.points[22] == 1

def test_apply_move_white():
    b = opening_board()
    new_b = apply_move(b, [(1, 7)], 'white')
    assert new_b.points[1] == -1
    assert new_b.points[7] == -1

# ── Move generation ──

def test_all_home_red_false_at_opening():
    b = opening_board()
    assert all_home(b, 'red') is False

def test_all_home_red_true():
    b = Board(points=[0]*25)
    b.points[3] = 3; b.points[5] = 2
    assert all_home(b, 'red') is True

def test_generate_moves_returns_list():
    b = opening_board()
    moves = generate_moves(b, [6, 1], 'red')
    assert isinstance(moves, list)
    assert len(moves) > 0

def test_generate_moves_uses_both_dice():
    b = opening_board()
    moves = generate_moves(b, [6, 1], 'red')
    assert all(len(m) == 2 for m in moves)

def test_generate_doubles_four_moves():
    b = opening_board()
    moves = generate_moves(b, [3, 3, 3, 3], 'red')
    assert all(len(m) == 4 for m in moves)

def test_generate_moves_bar_first():
    b = opening_board()
    b.red_bar = 1
    moves = generate_moves(b, [6, 1], 'red')
    assert all(m[0][0] == 0 for m in moves)

def test_generate_moves_no_landing_on_blocked():
    b = Board(points=[0]*25)
    b.points[24] = 2; b.points[20] = -2
    moves = generate_moves(b, [4, 1], 'red')
    for m in moves:
        for _, to_pt in m:
            assert to_pt != 20
