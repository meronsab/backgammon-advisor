let currentPlan = 'wise';
let pendingAdvicedMove = null;

document.querySelectorAll('.plan-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.plan-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentPlan = tab.dataset.plan;
  });
});

document.getElementById('new-game-btn').addEventListener('click', async () => {
  const data = await post('/api/new-game', {});
  updateBoard(data.board);
  updateAnalysis(data.analysis);
  clearHistory();
  document.getElementById('advice-result').style.display = 'none';
  document.getElementById('histogram').innerHTML = '<em style="color:#444">Get advice to see outcomes.</em>';
});

document.getElementById('advise-btn').addEventListener('click', async () => {
  const d1 = parseInt(document.getElementById('die1').value);
  const d2 = parseInt(document.getElementById('die2').value);
  if (!d1 || !d2 || d1 < 1 || d1 > 6 || d2 < 1 || d2 > 6) {
    alert('Enter two dice values (1–6).');
    return;
  }
  const data = await post('/api/advise', { dice: [d1, d2], plan: currentPlan });
  pendingAdvicedMove = data.best_move;
  document.getElementById('best-move-text').textContent = data.best_move || '—';
  document.getElementById('best-move-score').textContent = `Score: ${data.analysis.score}`;
  document.getElementById('advice-result').style.display = 'block';
  document.getElementById('override-box').classList.remove('visible');
  updateAnalysis(data.analysis);
  renderHistogram(data.histogram);
});

document.getElementById('take-btn').addEventListener('click', async () => {
  if (!pendingAdvicedMove || pendingAdvicedMove === '—') return;
  const data = await post('/api/apply-move', { move: pendingAdvicedMove });
  updateBoard(data.board);
  updateAnalysis(data.analysis);
  addHistoryEntry('you', pendingAdvicedMove);
  document.getElementById('advice-result').style.display = 'none';
  pendingAdvicedMove = null;
});

document.getElementById('override-btn').addEventListener('click', () => {
  document.getElementById('override-box').classList.toggle('visible');
});

document.getElementById('apply-override-btn').addEventListener('click', async () => {
  const move = document.getElementById('override-input').value.trim();
  if (!move) return;
  const data = await post('/api/apply-move', { move });
  updateBoard(data.board);
  updateAnalysis(data.analysis);
  addHistoryEntry('you', move);
  document.getElementById('advice-result').style.display = 'none';
  document.getElementById('override-input').value = '';
  pendingAdvicedMove = null;
});

document.getElementById('opp-apply-btn').addEventListener('click', async () => {
  const diceStr = document.getElementById('opp-dice').value.trim();
  const move = document.getElementById('opp-move').value.trim();
  if (!move) return;
  const dice = diceStr.split(/\s+/).map(Number).filter(n => n >= 1 && n <= 6);
  const data = await post('/api/opponent-move', { dice, move });
  updateBoard(data.board);
  updateAnalysis(data.analysis);
  addHistoryEntry('opp', move, diceStr);
  document.getElementById('opp-dice').value = '';
  document.getElementById('opp-move').value = '';
});

async function post(url, body) {
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return resp.json();
}

function updateAnalysis(a) {
  document.getElementById('win-pct').textContent = a.win_pct + '%';
  document.getElementById('gammon-pct').textContent = a.gammon_pct + '%';
  document.getElementById('bg-pct').textContent = a.backgammon_pct + '%';
  const cubeBox = document.getElementById('cube-box');
  cubeBox.className = 'cube-box ' + a.cube.action;
  const labels = { double: '💡 Double now', hold: '✋ Hold cube', beware: '⚠️ Watch out' };
  document.getElementById('cube-action').textContent = labels[a.cube.action] || a.cube.action;
  document.getElementById('cube-opp').textContent =
    a.cube.opponent_should !== 'n/a' ? `Opp: ${a.cube.opponent_should}` : '';
}

function updateBoard(board) {
  renderPoints(board);
  document.getElementById('bar-red').textContent = board.red_bar;
  document.getElementById('bar-white').textContent = board.white_bar;
  let redPip = 0, whitePip = 0;
  for (let i = 1; i <= 24; i++) {
    if (board.points[i] > 0) redPip += board.points[i] * i;
    if (board.points[i] < 0) whitePip += (-board.points[i]) * (25 - i);
  }
  document.getElementById('pip-red').textContent = redPip + board.red_bar * 25;
  document.getElementById('pip-white').textContent = whitePip + board.white_bar * 25;
}

function renderPoints(board) {
  const topRow = document.getElementById('top-row');
  const botRow = document.getElementById('bot-row');
  topRow.innerHTML = '';
  botRow.innerHTML = '';

  [13,14,15,16,17,18,null,19,20,21,22,23,24].forEach((pt, idx) => {
    if (pt === null) { topRow.appendChild(barSpacer()); return; }
    topRow.appendChild(makePoint(board.points[pt], idx % 2 === 0 ? 'dark' : 'light'));
  });

  [12,11,10,9,8,7,null,6,5,4,3,2,1].forEach((pt, idx) => {
    if (pt === null) { botRow.appendChild(barSpacer()); return; }
    botRow.appendChild(makePoint(board.points[pt], idx % 2 === 0 ? 'light' : 'dark'));
  });
}

function makePoint(count, triClass) {
  const div = document.createElement('div');
  div.className = 'point';
  const tri = document.createElement('div');
  tri.className = `point-triangle tri-${triClass}`;
  div.appendChild(tri);
  const color = count > 0 ? 'red' : 'white';
  for (let i = 0; i < Math.abs(count); i++) {
    const c = document.createElement('div');
    c.className = `checker ${color}`;
    div.appendChild(c);
  }
  return div;
}

function barSpacer() {
  const s = document.createElement('div');
  s.style.cssText = 'width:24px;flex-shrink:0';
  return s;
}

function renderHistogram(hist) {
  const el = document.getElementById('histogram');
  el.innerHTML = '';
  const maxAbs = Math.max(...hist.map(e => Math.abs(e.score)), 0.01);
  hist.forEach(entry => {
    const row = document.createElement('div');
    row.className = 'hist-entry';
    const pct = Math.round((Math.abs(entry.score) / maxAbs) * 100);
    const barClass = entry.score > 0.05 ? 'bar-pos' : entry.score < -0.05 ? 'bar-neg' : 'bar-neu';
    const valColor = entry.score > 0.05 ? '#2ecc71' : entry.score < -0.05 ? '#e74c3c' : '#f39c12';
    row.title = `Best: ${entry.best_move}`;
    row.innerHTML = `
      <span class="hist-dice">${entry.dice[0]}-${entry.dice[1]}</span>
      <div class="hist-bar-bg"><div class="hist-bar ${barClass}" style="width:${pct}%"></div></div>
      <span class="hist-val" style="color:${valColor}">${entry.score >= 0 ? '+' : ''}${entry.score.toFixed(2)}</span>
    `;
    el.appendChild(row);
  });
}

function addHistoryEntry(player, move, dice) {
  const log = document.getElementById('history-log');
  if (log.querySelector('em')) log.innerHTML = '';
  const div = document.createElement('div');
  div.className = `history-entry ${player}`;
  div.textContent = player === 'you' ? `You: ${move}` : `Opp: ${dice ? dice + ' → ' : ''}${move}`;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

function clearHistory() {
  document.getElementById('history-log').innerHTML = '<em style="color:#444">Move history will appear here.</em>';
}

(async () => {
  const resp = await fetch('/api/state');
  if (resp.ok) {
    const data = await resp.json();
    updateBoard(data.board);
    updateAnalysis(data.analysis);
    data.history.forEach(h => addHistoryEntry(h.player, h.move, h.dice ? h.dice.join(' ') : ''));
  } else {
    const data = await post('/api/new-game', {});
    updateBoard(data.board);
    updateAnalysis(data.analysis);
  }
})();
