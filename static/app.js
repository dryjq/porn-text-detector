async function postJSON(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || '请求失败');
  }
  return res.json();
}

async function loadProgress() {
  const res = await fetch('/api/progress');
  const data = await res.json();
  const total = data.total || 0;
  const completed = data.completed || 0;
  const percent = Math.round(data.percent || 0);
  document.getElementById('progress-fill').style.width = `${percent}%`;
  document.getElementById('progress-text').innerText = `${completed} / ${total}`;
  document.getElementById('pending-count').innerText = data.pending || 0;
  document.getElementById('running-count').innerText = data.in_progress || 0;
  document.getElementById('completed-count').innerText = completed;
  document.getElementById('failed-count').innerText = data.failed || 0;
  document.getElementById('hit-rate').innerText = `${Math.round((data.hit_rate || 0) * 100)}%`;
}

async function loadResults() {
  const res = await fetch('/api/results?limit=30');
  const res = await fetch('/api/results?limit=20');
  const data = await res.json();
  const body = document.getElementById('results-body');
  body.innerHTML = '';
  data.items.forEach((row) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${row.id}</td>
      <td class="mono">${row.url}</td>
      <td>${row.model}</td>
      <td>${row.score !== null ? row.score.toFixed(2) : '-'}</td>
      <td>${renderStatus(row)}</td>
      <td>${row.priority}</td>
      <td>${row.attempts}</td>
      <td>${row.message || ''}</td>
      <td>${row.url}</td>
      <td>${row.model}</td>
      <td>${row.score !== null ? row.score.toFixed(2) : '-'}</td>
      <td>${renderStatus(row)}</td>
      <td>${row.updated_at || ''}</td>
    `;
    body.appendChild(tr);
  });
}

async function loadQueue() {
  const res = await fetch('/api/queue?limit=50');
  const data = await res.json();
  const body = document.getElementById('queue-body');
  body.innerHTML = '';
  data.items.forEach((row) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${row.id}</td>
      <td class="mono">${row.url}</td>
      <td>${row.model}</td>
      <td>${row.priority}</td>
      <td>${row.attempts}</td>
      <td>${renderStatus(row)}</td>
      <td>${row.updated_at || ''}</td>
      <td>${row.message || ''}</td>
    `;
    body.appendChild(tr);
  });
}

function renderStatus(row) {
  if (row.status === 'completed') {
    return `<span class="tag ${row.is_porn ? 'danger' : 'success'}">${row.is_porn ? '命中' : '安全'}</span>`;
  }
  if (row.status === 'failed') {
    return '<span class="tag danger">失败</span>';
  }
  if (row.status === 'in_progress') return '<span class="tag muted">检测中</span>';
  return '<span class="tag muted">排队</span>';
}

async function submitUrls() {
  const urls = document.getElementById('urls').value;
  const model = document.getElementById('model').value;
  const priority = document.getElementById('priority').value;
  const btn = document.getElementById('submit-btn');
  btn.setAttribute('aria-busy', 'true');
  try {
    await postJSON('/api/enqueue', { urls, model, priority });
    document.getElementById('urls').value = '';
    await loadProgress();
    await loadResults();
    await loadQueue();
  const btn = document.getElementById('submit-btn');
  btn.setAttribute('aria-busy', 'true');
  try {
    await postJSON('/api/enqueue', { urls, model });
    document.getElementById('urls').value = '';
    await loadProgress();
    await loadResults();
  } catch (err) {
    alert(err.message);
  } finally {
    btn.removeAttribute('aria-busy');
  }
}

async function loadSeeds() {
  const res = await fetch('/api/seeds');
  const data = await res.json();
  document.getElementById('seed-list').innerText = data.domains.join(', ') || '(未配置)';
}

async function saveSeeds() {
  const raw = document.getElementById('seed-input').value || '';
  const domains = raw.split(',').map((s) => s.trim()).filter(Boolean);
  const btn = document.getElementById('seed-save');
  btn.setAttribute('aria-busy', 'true');
  try {
    await postJSON('/api/seeds', { domains });
    await loadSeeds();
  } catch (err) {
    alert(err.message);
  } finally {
    btn.removeAttribute('aria-busy');
  }
}

async function retryFailed() {
  const btn = document.getElementById('retry-btn');
  btn.setAttribute('aria-busy', 'true');
  try {
    await postJSON('/api/retry_failed', {});
    await loadProgress();
    await loadQueue();
  } catch (err) {
    alert(err.message);
  } finally {
    btn.removeAttribute('aria-busy');
  }
}

async function purgeCompleted() {
  const btn = document.getElementById('purge-btn');
  btn.setAttribute('aria-busy', 'true');
  try {
    await postJSON('/api/purge_completed', {});
    await loadProgress();
    await loadQueue();
    await loadResults();
  } catch (err) {
    alert(err.message);
  } finally {
    btn.removeAttribute('aria-busy');
  }
}

document.getElementById('submit-btn').addEventListener('click', submitUrls);
document.getElementById('seed-save').addEventListener('click', saveSeeds);
document.getElementById('retry-btn').addEventListener('click', retryFailed);
document.getElementById('purge-btn').addEventListener('click', purgeCompleted);

actionHooks();

async function actionHooks() {
  await loadProgress();
  await loadResults();
  await loadQueue();
  await loadSeeds();
  setInterval(loadProgress, 2000);
  setInterval(loadQueue, 3000);
  setInterval(loadResults, 5000);
}
document.getElementById('submit-btn').addEventListener('click', submitUrls);
document.getElementById('seed-save').addEventListener('click', saveSeeds);

loadProgress();
loadResults();
loadSeeds();
setInterval(loadProgress, 2000);
setInterval(loadResults, 5000);
