(function () {
    const logWindow = document.getElementById('training-log');
    const statusBadge = document.getElementById('training-status');
    const modelSelect = document.getElementById('model-select');
    const datasetSelect = document.getElementById('dataset-select');
    const trainingForm = document.getElementById('training-form');
    const loadExperimentsBtn = document.getElementById('load-experiments');
    const refreshExperimentsBtn = document.getElementById('refresh-experiments');
    const experimentTableBody = document.querySelector('#experiment-table tbody');
    const metricsCanvas = document.getElementById('metrics-chart');

    const state = {
        logTimer: null,
        chart: null,
        lastLogId: null,
    };

    document.addEventListener('DOMContentLoaded', () => {
        bindTabSwitcher();
        loadModels();
        loadDatasets();
        attachFormHandler();
        attachExperimentButtons();
    });

    function bindTabSwitcher() {
        const buttons = document.querySelectorAll('.tab-button');
        const panels = document.querySelectorAll('.tab-panel');

        buttons.forEach((btn) => {
            btn.addEventListener('click', () => {
                buttons.forEach((b) => b.classList.remove('active'));
                panels.forEach((p) => p.classList.remove('active'));
                btn.classList.add('active');
                const target = document.getElementById(btn.dataset.target);
                if (target) target.classList.add('active');
            });
        });
    }

    async function loadModels() {
        try {
            const response = await fetch('/api/models');
            if (!response.ok) throw new Error('加载模型失败');
            const data = await response.json();
            populateSelect(modelSelect, data, 'name', 'label');
        } catch (err) {
            console.warn('加载模型失败', err);
            populateSelect(modelSelect, [], 'name', 'label');
        }
    }

    async function loadDatasets() {
        try {
            const response = await fetch('/api/datasets');
            if (!response.ok) throw new Error('加载数据集失败');
            const data = await response.json();
            populateSelect(datasetSelect, data, 'name', 'label');
        } catch (err) {
            console.warn('加载数据集失败', err);
            populateSelect(datasetSelect, [], 'name', 'label');
        }
    }

    function populateSelect(selectEl, list, valueKey, labelKey) {
        if (!selectEl) return;
        const fragment = document.createDocumentFragment();
        const placeholder = document.createElement('option');
        placeholder.textContent = selectEl.options[0]?.textContent || '请选择';
        placeholder.disabled = true;
        placeholder.selected = true;
        placeholder.value = '';
        fragment.appendChild(placeholder);

        if (Array.isArray(list) && list.length) {
            list.forEach((item) => {
                const option = document.createElement('option');
                option.value = item[valueKey] ?? item;
                option.textContent = item[labelKey] ?? item[valueKey] ?? item;
                fragment.appendChild(option);
            });
        }

        selectEl.innerHTML = '';
        selectEl.appendChild(fragment);
    }

    function attachFormHandler() {
        if (!trainingForm) return;
        trainingForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(trainingForm);
            const payload = {
                model: formData.get('model'),
                dataset: formData.get('dataset'),
                hyperparameters: {
                    learning_rate: Number(formData.get('learning_rate')),
                    epochs: Number(formData.get('epochs')),
                    batch_size: Number(formData.get('batch_size')),
                    weight_decay: Number(formData.get('weight_decay')),
                },
            };

            updateStatusBadge('running');
            appendLog('开始提交训练任务...');

            try {
                const response = await fetch('/api/train', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                });

                if (!response.ok) throw new Error('训练请求失败');
                appendLog('训练任务已启动，正在获取日志...');
                startLogPolling();
                loadExperiments();
            } catch (err) {
                console.error(err);
                appendLog('训练启动失败：' + err.message);
                updateStatusBadge('error');
            }
        });
    }

    function attachExperimentButtons() {
        loadExperimentsBtn?.addEventListener('click', loadExperiments);
        refreshExperimentsBtn?.addEventListener('click', loadExperiments);
    }

    function startLogPolling() {
        stopLogPolling();
        state.logTimer = setInterval(fetchLogUpdates, 4000);
        fetchLogUpdates();
    }

    function stopLogPolling() {
        if (state.logTimer) {
            clearInterval(state.logTimer);
            state.logTimer = null;
        }
    }

    async function fetchLogUpdates() {
        try {
            const response = await fetch('/api/train/status');
            if (!response.ok) throw new Error('无法获取训练状态');
            const data = await response.json();
            updateStatusBadge(data.status || 'running');
            appendLogs(data.logs || []);

            if (data.status && ['completed', 'failed', 'idle'].includes(data.status)) {
                stopLogPolling();
                loadExperiments();
            }
        } catch (err) {
            console.warn('获取日志失败', err);
            appendLog('获取日志失败：' + err.message);
        }
    }

    function appendLogs(logs) {
        if (!Array.isArray(logs) || !logs.length) return;
        logs.forEach((entry) => {
            if (entry.id && entry.id === state.lastLogId) return;
            appendLog(entry.message || entry);
            state.lastLogId = entry.id || state.lastLogId;
        });
    }

    function appendLog(message) {
        if (!logWindow) return;
        const time = new Date().toLocaleTimeString();
        const paragraph = document.createElement('p');
        paragraph.textContent = `[${time}] ${message}`;
        logWindow.appendChild(paragraph);
        logWindow.scrollTop = logWindow.scrollHeight;
    }

    function updateStatusBadge(status) {
        if (!statusBadge) return;
        statusBadge.className = 'status-badge';
        switch (status) {
            case 'running':
                statusBadge.classList.add('running');
                statusBadge.textContent = '训练中';
                break;
            case 'completed':
                statusBadge.classList.add('success');
                statusBadge.textContent = '已完成';
                break;
            case 'failed':
                statusBadge.classList.add('error');
                statusBadge.textContent = '失败';
                break;
            default:
                statusBadge.classList.add('idle');
                statusBadge.textContent = '待机';
        }
    }

    async function loadExperiments() {
        try {
            const response = await fetch('/api/experiments');
            if (!response.ok) throw new Error('加载实验失败');
            const experiments = await response.json();
            renderExperimentTable(experiments);
            renderMetricsChart(experiments);
        } catch (err) {
            console.error(err);
            renderExperimentTable([]);
            appendLog('加载实验失败：' + err.message);
        }
    }

    function renderExperimentTable(experiments) {
        if (!experimentTableBody) return;
        experimentTableBody.innerHTML = '';
        if (!Array.isArray(experiments) || !experiments.length) {
            const emptyRow = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = 8;
            cell.textContent = '暂无实验记录';
            cell.className = 'muted';
            emptyRow.appendChild(cell);
            experimentTableBody.appendChild(emptyRow);
            return;
        }

        experiments.forEach((exp) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${exp.id ?? '-'}</td>
                <td>${exp.model ?? '-'}</td>
                <td>${exp.dataset ?? '-'}</td>
                <td>${exp.learning_rate ?? exp.hyperparameters?.learning_rate ?? '-'}</td>
                <td>${exp.epochs ?? exp.hyperparameters?.epochs ?? '-'}</td>
                <td>${exp.batch_size ?? exp.hyperparameters?.batch_size ?? '-'}</td>
                <td>${exp.status ?? '-'}</td>
                <td>${formatMetrics(exp.metrics)}</td>
            `;
            experimentTableBody.appendChild(row);
        });
    }

    function formatMetrics(metrics) {
        if (!metrics) return '-';
        if (typeof metrics === 'string') return metrics;
        if (typeof metrics === 'object') {
            return Object.entries(metrics)
                .map(([key, value]) => `${key}: ${value}`)
                .join(' | ');
        }
        return '-';
    }

    function renderMetricsChart(experiments) {
        if (!metricsCanvas) return;
        if (!window.Chart) {
            metricsCanvas.replaceWith(textFallback('未找到 Chart.js，可通过表格查看指标。'));
            return;
        }

        const { labels, datasets } = buildChartData(experiments);
        if (!labels.length || !datasets.length) {
            metricsCanvas.replaceWith(textFallback('暂无可视化指标数据'));
            return;
        }

        if (state.chart) state.chart.destroy();
        state.chart = new Chart(metricsCanvas, {
            type: 'line',
            data: {
                labels,
                datasets,
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 3,
                        },
                    },
                },
            },
        });
    }

    function buildChartData(experiments) {
        if (!Array.isArray(experiments) || !experiments.length) {
            return { labels: [], datasets: [] };
        }

        const labels = experiments.map((exp) => `实验${exp.id ?? ''}`.trim());
        const metricKeys = Object.keys(experiments[0].metrics || {});

        const datasets = metricKeys.map((key, idx) => ({
            label: key,
            data: experiments.map((exp) => exp.metrics?.[key] ?? null),
            borderColor: colorPalette(idx),
            tension: 0.3,
            spanGaps: true,
        }));

        return { labels, datasets };
    }

    function colorPalette(index) {
        const colors = [
            '#3b82f6',
            '#10b981',
            '#f59e0b',
            '#ef4444',
            '#8b5cf6',
            '#0ea5e9',
        ];
        return colors[index % colors.length];
    }

    function textFallback(text) {
        const div = document.createElement('div');
        div.className = 'chart-fallback';
        div.textContent = text;
        return div;
    }
})();
