async function fetchStats() {
  const res = await fetch('/api/stats');
  return res.json();
}

function buildLineChart(ctx, labels, data, label, color) {
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label,
          data,
          fill: false,
          borderColor: color,
          tension: 0.2,
        },
      ],
    },
  });
}

function buildBarChart(ctx, labels, data, label, color) {
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label,
          data,
          backgroundColor: color,
        },
      ],
    },
  });
}

function buildPie(ctx, labels, data) {
  return new Chart(ctx, {
    type: 'pie',
    data: {
      labels,
      datasets: [
        {
          data,
          backgroundColor: ['#22c55e', '#eab308', '#f97316', '#ef4444', '#38bdf8'],
        },
      ],
    },
  });
}

async function render() {
  const stats = await fetchStats();
  const dailyLabels = stats.daily.map((x) => x.day);
  const dailyTotals = stats.daily.map((x) => x.total);
  const dailyHits = stats.daily.map((x) => x.hits);

  buildLineChart(document.getElementById('daily-chart'), dailyLabels, dailyTotals, '检测数量', '#3b82f6');
  buildLineChart(document.getElementById('model-chart'), stats.models.map((m) => m.model), stats.models.map((m) => m.c), '调用次数', '#a855f7');
  buildBarChart(document.getElementById('domain-chart'), stats.domains.map((d) => d.domain), stats.domains.map((d) => d.total), '域名出现次数', '#f97316');

  const latencyLabels = Object.keys(stats.latency);
  const latencyValues = latencyLabels.map((k) => stats.latency[k]);
  buildBarChart(document.getElementById('latency-chart'), latencyLabels, latencyValues, '耗时分布', '#22c55e');

  const statusLabels = Object.keys(stats.statuses);
  const statusValues = statusLabels.map((k) => stats.statuses[k]);
  buildPie(document.getElementById('status-chart'), statusLabels, statusValues);
}

render();
