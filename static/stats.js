async function fetchStats() {
  const res = await fetch('/api/stats');
  return res.json();
}

function renderDailyChart(ctx, data) {
  const labels = data.map((d) => d.day);
  const totals = data.map((d) => d.total);
  const hits = data.map((d) => d.hits);
  new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: '检测数量', data: totals, borderColor: '#2563eb', tension: 0.2 },
        { label: '命中数量', data: hits, borderColor: '#dc2626', tension: 0.2 },
      ],
    },
    options: { responsive: true },
  });
}

function renderModelChart(ctx, data) {
  const labels = data.map((d) => d.model || '未指定');
  const totals = data.map((d) => d.total);
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: '调用次数', data: totals, backgroundColor: '#0ea5e9' },
      ],
    },
    options: { responsive: true },
  });
}

async function init() {
  const data = await fetchStats();
  document.getElementById('hit-rate-text').innerText = `${Math.round((data.hit_rate || 0) * 100)}%`;
  renderDailyChart(document.getElementById('daily-chart'), data.daily_counts || []);
  renderModelChart(document.getElementById('model-chart'), data.model_usage || []);
}

init();
