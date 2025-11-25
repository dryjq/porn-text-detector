async function loadEvents() {
  const res = await fetch('/api/events?limit=200');
  const data = await res.json();
  const body = document.getElementById('events-body');
  body.innerHTML = '';
  data.items.forEach((row) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${row.id}</td>
      <td class="mono">${row.url || '-'}</td>
      <td>${row.event}</td>
      <td>${row.payload}</td>
      <td>${row.created_at}</td>
    `;
    body.appendChild(tr);
  });
}

loadEvents();
setInterval(loadEvents, 5000);
