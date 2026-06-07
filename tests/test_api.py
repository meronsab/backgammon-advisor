import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test'
    with app.test_client() as c:
        yield c

def test_new_game(client):
    resp = client.post('/api/new-game')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'board' in data
    assert data['board']['red_bar'] == 0

def test_get_state_after_new_game(client):
    client.post('/api/new-game')
    resp = client.get('/api/state')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'board' in data
    assert 'analysis' in data

def test_advise(client):
    client.post('/api/new-game')
    resp = client.post('/api/advise', json={'dice': [6, 1], 'plan': 'wise'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'best_move' in data
    assert 'histogram' in data
    assert 'analysis' in data

def test_apply_move(client):
    client.post('/api/new-game')
    resp = client.post('/api/apply-move', json={'move': '13/7 8/7'})
    assert resp.status_code == 200
    assert 'board' in resp.get_json()

def test_opponent_move(client):
    client.post('/api/new-game')
    resp = client.post('/api/opponent-move', json={'dice': [3, 1], 'move': '8/5 6/5'})
    assert resp.status_code == 200

def test_get_state_no_session_returns_400(client):
    resp = client.get('/api/state')
    assert resp.status_code == 400
