let currentPlan = 'wise';
let pendingAdvicedMove = null;

function expandDice(d1, d2) {
  return d1 === d2 ? [d1, d2, d1, d2] : [d1, d2];
}
let currentBoard = null;
let clickMoveState = null;
let highlightedPoints = { from: new Set(), to: new Set(), clickable: new Set(), selected: new Set(), target: new Set() };

// ── Plan tabs ──
document.querySelectorAll('.plan-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.plan-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentPlan = tab.dataset.plan;
  });
});

// ── New game ──
document.getElementById('new-game-btn').addEventListener('click', async () => {
  const data = await post('/api/new-game', {});
  cancelClickMove();
  updateBoard(data.board);
  updateAnalysis(data.analysis);
  clearHistory();
  document.getElementById('advice-result').style.display = 'none';
  document.getElementById('histogram').innerHTML = '<em style="color:#444">Get advice to see outcomes.</em>';
});

// ── Get advice (also Enter key) ──
document.getElementById('advise-btn').addEventListener('click', getAdvice);
document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && document.activeElement.closest('.dice-row')) getAdvice();
  if (e.key === 'Escape') cancelClickMove();
});

async function getAdvice() {
  const d1 = parseInt(document.getElementById('die1').value);
  const d2 = parseInt(document.getElementById('die2').value);
  if (!d1 || !d2 || d1 < 1 || d1 > 6 || d2 < 1 || d2 > 6) {
    alert('Enter two dice values (1–6).');
    return;
  }
  cancelClickMove();
  setAdvising(true);
  const data = await post('/api/advise', { dice: expandDice(d1, d2), plan: currentPlan });
  setAdvising(false);
  pendingAdvicedMove = data.best_move;
  document.getElementById('best-move-text').textContent = data.best_move || '—';
  document.getElementById('best-move-score').textContent = `Score: ${data.analysis.score}`;
  document.getElementById('advice-result').style.display = 'block';
  document.getElementById('override-box').classList.remove('visible');
  updateAnalysis(data.analysis);
  renderHistogram(data.histogram);
  const { from, to } = parseMovePoints(data.best_move);
  highlightedPoints.from = new Set(from);
  highlightedPoints.to = new Set(to);
  if (currentBoard) renderPoints(currentBoard);
  showClickHint(false);
}

function setAdvising(on) {
  document.getElementById('advise-spinner').style.display = on ? 'inline-block' : 'none';
  document.getElementById('advise-text').textContent = on ? 'Thinking…' : 'Get Advice';
  document.getElementById('advise-btn').disabled = on;
}

// ── Take advice ──
document.getElementById('take-btn').addEventListener('click', async () => {
  if (!pendingAdvicedMove || pendingAdvicedMove === '—') return;
  const data = await post('/api/apply-move', { move: pendingAdvicedMove });
  clearHighlights();
  updateBoard(data.board);
  updateAnalysis(data.analysis);
  addHistoryEntry('you', pendingAdvicedMove);
  document.getElementById('advice-result').style.display = 'none';
  pendingAdvicedMove = null;
});

// ── Override ──
document.getElementById('override-btn').addEventListener('click', () => {
  document.getElementById('override-box').classList.toggle('visible');
});

document.getElementById('apply-override-btn').addEventListener('click', async () => {
  const move = document.getElementById('override-input').value.trim();
  if (!move) return;
  const data = await post('/api/apply-move', { move });
  clearHighlights();
  updateBoard(data.board);
  updateAnalysis(data.analysis);
  addHistoryEntry('you', move);
  document.getElementById('advice-result').style.display = 'none';
  document.getElementById('override-input').value = '';
  pendingAdvicedMove = null;
});

// ── Opponent move ──
document.getElementById('opp-apply-btn').addEventListener('click', async () => {
  const diceStr = document.getElementById('opp-dice').value.trim();
  const move = document.getElementById('opp-move').value.trim();
  if (!move) return;
  const dice = diceStr.split(/\s+/).map(Number).filter(n => n >= 1 && n <= 6);
  const data = await post('/api/opponent-move', { dice, move });
  clearHighlights();
  cancelClickMove();
  updateBoard(data.board);
  updateAnalysis(data.analysis);
  addHistoryEntry('opp', move, diceStr);
  document.getElementById('opp-dice').value = '';
  document.getElementById('opp-move').value = '';
});

// ── Click-to-move ──
document.getElementById('top-row').addEventListener('click', handleBoardClick);
document.getElementById('bot-row').addEventListener('click', handleBoardClick);

async function handleBoardClick(e) {
  const pointEl = e.target.closest('.point[data-pt]');
  if (!pointEl) return;
  const pt = parseInt(pointEl.dataset.pt);
  if (!currentBoard) return;

  const isRedChecker   = currentBoard.points[pt] > 0;
  const isWhiteChecker = currentBoard.points[pt] < 0;

  if (!clickMoveState) {
    // Start red click-to-move
    if (isRedChecker) {
      const d1 = parseInt(document.getElementById('die1').value);
      const d2 = parseInt(document.getElementById('die2').value);
      if (!d1 || !d2) return;
      const data = await post('/api/legal-moves', { dice: expandDice(d1, d2), player: 'red' });
      const legalMoves = data.moves.map(m => m.submoves);
      if (!legalMoves.length) return;
      clearHighlights();
      clickMoveState = { player: 'red', legalMoves, remainingMoves: legalMoves, partialMoves: [], step: 0, selectedFrom: null };
      document.getElementById('advice-result').style.display = 'none';
      showClickHint(true);
      selectFromPoint(pt);
      return;
    }
    // Start white (opponent) click-to-move
    if (isWhiteChecker) {
      const diceStr = document.getElementById('opp-dice').value.trim();
      const oppDice = diceStr.split(/\s+/).map(Number).filter(n => n >= 1 && n <= 6);
      if (oppDice.length < 2) return;
      const data = await post('/api/legal-moves', { dice: expandDice(oppDice[0], oppDice[1]), player: 'white' });
      const legalMoves = data.moves.map(m => m.submoves);
      if (!legalMoves.length) return;
      clearHighlights();
      clickMoveState = { player: 'white', legalMoves, remainingMoves: legalMoves, partialMoves: [], step: 0, selectedFrom: null };
      showClickHint(true);
      selectFromPoint(pt);
      return;
    }
    return;
  }

  if (clickMoveState.selectedFrom === null) {
    selectFromPoint(pt);
  } else {
    const targets = getValidToPoints(clickMoveState.remainingMoves, clickMoveState.step, clickMoveState.selectedFrom);
    if (targets.has(pt)) {
      await completeSubMove(clickMoveState.selectedFrom, pt);
    } else if (getValidFromPoints(clickMoveState.remainingMoves, clickMoveState.step).has(pt)) {
      selectFromPoint(pt);
    } else {
      cancelClickMove();
    }
  }
}

function getValidFromPoints(moves, step) {
  return new Set(moves.filter(m => m.length > step).map(m => m[step][0]));
}

function getValidToPoints(moves, step, fromPt) {
  return new Set(moves.filter(m => m.length > step && m[step][0] === fromPt).map(m => m[step][1]));
}

function selectFromPoint(pt) {
  if (!clickMoveState) return;
  const validFrom = getValidFromPoints(clickMoveState.remainingMoves, clickMoveState.step);
  if (!validFrom.has(pt)) { cancelClickMove(); return; }
  clickMoveState.selectedFrom = pt;
  const targets = getValidToPoints(clickMoveState.remainingMoves, clickMoveState.step, pt);
  highlightedPoints.clickable = new Set();
  highlightedPoints.selected = new Set([pt]);
  highlightedPoints.target = targets;
  if (currentBoard) renderPoints(currentBoard);
}

async function completeSubMove(fromPt, toPt) {
  clickMoveState.partialMoves.push([fromPt, toPt]);
  clickMoveState.step++;
  clickMoveState.remainingMoves = clickMoveState.remainingMoves.filter(m => {
    if (m.length < clickMoveState.step) return false;
    for (let i = 0; i < clickMoveState.step; i++) {
      if (m[i][0] !== clickMoveState.partialMoves[i][0] || m[i][1] !== clickMoveState.partialMoves[i][1]) return false;
    }
    return true;
  });

  const done = clickMoveState.remainingMoves.every(m => m.length <= clickMoveState.step);
  if (done) {
    const player = clickMoveState.player;
    const bar = player === 'red' ? 0 : 25;
    const off = player === 'red' ? 0 : 25;
    const moveStr = clickMoveState.partialMoves
      .map(([f, t]) => `${f === bar ? 'bar' : f}/${t === off ? 'off' : t}`)
      .join(' ');
    cancelClickMove();
    let data;
    if (player === 'red') {
      data = await post('/api/apply-move', { move: moveStr });
      clearHighlights();
      updateBoard(data.board);
      updateAnalysis(data.analysis);
      addHistoryEntry('you', moveStr);
    } else {
      const diceStr = document.getElementById('opp-dice').value.trim();
      const oppDice = diceStr.split(/\s+/).map(Number).filter(n => n >= 1 && n <= 6);
      data = await post('/api/opponent-move', { dice: oppDice, move: moveStr });
      clearHighlights();
      updateBoard(data.board);
      updateAnalysis(data.analysis);
      addHistoryEntry('opp', moveStr, diceStr);
      document.getElementById('opp-dice').value = '';
      document.getElementById('opp-move').value = '';
    }
    showClickHint(false);
    return;
  }

  clickMoveState.selectedFrom = null;
  const fromPts = getValidFromPoints(clickMoveState.remainingMoves, clickMoveState.step);
  highlightedPoints.selected = new Set();
  highlightedPoints.target = new Set();
  highlightedPoints.clickable = fromPts;
  if (currentBoard) renderPoints(currentBoard);
}

function cancelClickMove() {
  clickMoveState = null;
  showClickHint(false);
  clearHighlights();
  if (currentBoard) renderPoints(currentBoard);
}

function showClickHint(on) {
  document.getElementById('click-hint').style.display = on ? 'block' : 'none';
}

// ── Helpers ──
async function post(url, body) {
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return resp.json();
}

function parseMovePoints(moveStr) {
  const from = [], to = [];
  if (!moveStr || moveStr === '—') return { from, to };
  moveStr.split(' ').forEach(part => {
    const [src, dst] = part.split('/');
    if (src && src.toLowerCase() !== 'bar') { const p = parseInt(src); if (!isNaN(p)) from.push(p); }
    if (dst && dst.toLowerCase() !== 'off') { const p = parseInt(dst); if (!isNaN(p)) to.push(p); }
  });
  return { from, to };
}

function clearHighlights() {
  highlightedPoints = { from: new Set(), to: new Set(), clickable: new Set(), selected: new Set(), target: new Set() };
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
  currentBoard = board;
  renderPoints(board);
  document.getElementById('bar-red').textContent = board.red_bar;
  document.getElementById('bar-white').textContent = board.white_bar;
  document.getElementById('off-red').textContent = board.red_off;
  document.getElementById('off-white').textContent = board.white_off;

  let redPip = 0, whitePip = 0;
  for (let i = 1; i <= 24; i++) {
    if (board.points[i] > 0) redPip += board.points[i] * i;
    if (board.points[i] < 0) whitePip += (-board.points[i]) * (25 - i);
  }
  redPip += board.red_bar * 25;
  whitePip += board.white_bar * 25;
  document.getElementById('pip-red').textContent = redPip;
  document.getElementById('pip-white').textContent = whitePip;

  const delta = whitePip - redPip;
  const deltaEl = document.getElementById('pip-delta');
  if (delta > 0) {
    deltaEl.textContent = `You lead +${delta}`;
    deltaEl.className = 'pip-delta red-leads';
  } else if (delta < 0) {
    deltaEl.textContent = `Behind ${delta}`;
    deltaEl.className = 'pip-delta white-leads';
  } else {
    deltaEl.textContent = 'Even';
    deltaEl.className = 'pip-delta';
  }
}

function renderPoints(board) {
  const topRow = document.getElementById('top-row');
  const botRow = document.getElementById('bot-row');
  topRow.innerHTML = '';
  botRow.innerHTML = '';

  [13,14,15,16,17,18,null,19,20,21,22,23,24].forEach((pt, idx) => {
    if (pt === null) { topRow.appendChild(barSpacer()); return; }
    topRow.appendChild(makePoint(pt, board.points[pt], 'top', idx % 2 === 0 ? 'dark' : 'light'));
  });

  [12,11,10,9,8,7,null,6,5,4,3,2,1].forEach((pt, idx) => {
    if (pt === null) { botRow.appendChild(barSpacer()); return; }
    botRow.appendChild(makePoint(pt, board.points[pt], 'bot', idx % 2 === 0 ? 'light' : 'dark'));
  });
}

function makePoint(pt, count, rowType, triClass) {
  const hlClass =
    highlightedPoints.selected.has(pt)  ? 'hl-selected' :
    highlightedPoints.target.has(pt)    ? 'hl-target' :
    highlightedPoints.clickable.has(pt) ? 'hl-clickable' :
    highlightedPoints.from.has(pt)      ? 'highlight-from' :
    highlightedPoints.to.has(pt)        ? 'highlight-to' : '';

  const div = document.createElement('div');
  div.className = 'point' + (hlClass ? ` ${hlClass}` : '');
  div.dataset.pt = pt;

  const tri = document.createElement('div');
  tri.className = `point-triangle tri-${triClass}`;
  div.appendChild(tri);

  const ptNum = document.createElement('span');
  ptNum.className = 'pt-num';
  ptNum.textContent = pt;
  div.appendChild(ptNum);

  const n = Math.abs(count);
  if (n === 0) return div;
  const color = count > 0 ? 'red' : 'white';
  const overflow = n > 5;
  const numCheckers = overflow ? 5 : n;

  const makeBadge = () => {
    const b = document.createElement('div');
    b.className = 'checker-badge';
    b.textContent = n;
    return b;
  };

  if (overflow && rowType === 'bot') div.appendChild(makeBadge());
  for (let i = 0; i < numCheckers; i++) {
    const c = document.createElement('div');
    c.className = `checker ${color}`;
    div.appendChild(c);
  }
  if (overflow && rowType === 'top') div.appendChild(makeBadge());

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
