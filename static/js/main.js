function getModelSelection() {
    const radios = document.querySelectorAll('input[name="model-option"]');
    for (const r of radios) {
        if (r.checked) return r.value;
    }
    return 'fasttext';
}

function renderTable(containerId, results) {
    const tbody = document.querySelector(containerId);
    tbody.innerHTML = '';
    results.forEach((item, idx) => {
        const badgeClass = item.label === '色情' ? 'badge-danger' : (item.label === '正常' ? 'badge-success' : 'badge-secondary');
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${idx + 1}</td>
            <td>${item.url}</td>
            <td><span class="badge ${badgeClass}">${item.label}</span></td>
            <td>${item.proba}</td>
            <td>${item.model}</td>
            <td>${item.success ? '成功' : '失败'}</td>
            <td>${item.error || ''}</td>`;
        tbody.appendChild(row);
    });
}

function showAlert(message, type = 'danger') {
    const alertBox = document.getElementById('alert-box');
    alertBox.innerHTML = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>`;
}

async function classifyText() {
    const text = document.getElementById('single-text').value;
    const model = getModelSelection();
    if (!text.trim()) return showAlert('请输入待测文本');
    const resp = await fetch('/api/classify-text', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text, model})
    });
    const data = await resp.json();
    if (!resp.ok) return showAlert(data.error || '请求失败');
    renderTable('#single-result tbody', [data]);
}

async function classifyUrls(formId, tableId) {
    const form = document.getElementById(formId);
    const model = getModelSelection();
    const formData = new FormData(form);
    formData.append('model', model);
    const resp = await fetch('/api/classify-urls', {method: 'POST', body: formData});
    const data = await resp.json();
    if (!resp.ok) return showAlert(data.error || '处理失败');
    renderTable(tableId, data.results);
}

async function loadHistory() {
    const resp = await fetch('/api/history');
    const data = await resp.json();
    renderTable('#history-table tbody', data);
}

document.addEventListener('DOMContentLoaded', () => {
    const textBtn = document.getElementById('btn-text');
    if (textBtn) textBtn.addEventListener('click', classifyText);

    const batchForm = document.getElementById('batch-form');
    if (batchForm) batchForm.addEventListener('submit', (e) => { e.preventDefault(); classifyUrls('batch-form', '#batch-result tbody'); });

    const onlineForm = document.getElementById('online-form');
    if (onlineForm) onlineForm.addEventListener('submit', (e) => { e.preventDefault(); classifyUrls('online-form', '#online-result tbody'); });

    loadHistory();
});
