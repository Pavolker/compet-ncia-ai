// ===================================
// ESHMIA Index Monitor - JavaScript
// Dashboard Logic & API Integration
// ===================================

// Configuration
const CONFIG = {
    apiUrl: 'data.json', // Updated for Netlify static deployment
    refreshInterval: 30000, // 30 seconds
    chartColors: {
        primary: '#667eea',
        secondary: '#764ba2',
        success: '#4facfe',
        warning: '#fa709a',
        info: '#00f2fe',
        gradients: [
            'rgba(102, 126, 234, 0.8)',
            'rgba(240, 147, 251, 0.8)',
            'rgba(79, 172, 254, 0.8)',
            'rgba(250, 112, 154, 0.8)',
        ]
    }
};

// Global state
let eshmiaChart = null;
let metricsChart = null;
let autoRefreshTimer = null;

// ===================================
// Initialization
// ===================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 ESHMIA Index Monitor initialized');

    // Setup event listeners
    setupEventListeners();

    // Load initial data
    loadData();

    // Start auto-refresh
    // startAutoRefresh(); // Desabilitado pois os dados são estáticos (CSV)
});

// ===================================
// Event Listeners
// ===================================

function setupEventListeners() {
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loadData();
            animateRefreshButton();
        });
    }
}

function animateRefreshButton() {
    const btn = document.getElementById('refreshBtn');
    btn.classList.add('spinning');
    setTimeout(() => btn.classList.remove('spinning'), 1000);
}

// ===================================
// Data Loading
// ===================================

async function loadData(silent = false) {
    try {
        if (!silent) showLoading(true);
        updateConnectionStatus('loading');

        const response = await fetch(CONFIG.apiUrl);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('📊 Data loaded:', data);

        // Update all sections
        updateHeroStats(data);
        updateCharts(data);
        updateModelsGrid(data);
        updateLeaderboard(data);
        updateMetricsExplanation(data);
        updateAnalysis(data);

        updateConnectionStatus('connected');
        showLoading(false);

    } catch (error) {
        console.error('❌ Error loading data:', error);
        updateConnectionStatus('error');
        showError(error.message);
        showLoading(false);
    }
}

// ===================================
// UI Updates
// ===================================

function updateHeroStats(data) {
    // ESHMIA Average
    const eshmiaAvg = document.getElementById('eshmiaAverage');
    if (eshmiaAvg && data.eshmia_medio) {
        eshmiaAvg.textContent = data.eshmia_medio.toFixed(4);

        // Add trend indicator
        const trend = data.eshmia_medio > 1 ? '↑' : '↓';
        const trendColor = data.eshmia_medio > 1 ? '#00f2fe' : '#fa709a';
        const trendElement = document.getElementById('eshmiaTrend');
        if (trendElement) {
            const percentage = ((data.eshmia_medio - 1) * 100).toFixed(2);
            trendElement.innerHTML = `<span style="color: ${trendColor}">${trend} ${Math.abs(percentage)}% vs baseline</span>`;
        }
    }

    // Model Count
    const modelCount = document.getElementById('modelCount');
    if (modelCount && data.lista_modelos) {
        modelCount.textContent = data.lista_modelos.length;
    }

    // Last Update
    const lastUpdate = document.getElementById('lastUpdate');
    const lastUpdateTime = document.getElementById('lastUpdateTime');
    if (lastUpdate && data.timestamp) {
        const date = new Date(data.timestamp);
        lastUpdate.textContent = date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: 'long',
            year: 'numeric'
        });
        if (lastUpdateTime) lastUpdateTime.style.display = 'none';
    }
}

function updateCharts(data) {
    if (!data.lista_modelos || data.lista_modelos.length === 0) {
        console.warn('⚠️ No model data available for charts');
        return;
    }

    // Sort models by ESHMIA
    const sortedModels = [...data.lista_modelos].sort((a, b) =>
        (b.valor_eshmia || 0) - (a.valor_eshmia || 0)
    );

    updateEshmiaChart(sortedModels);
    updateMetricsChart(sortedModels);
}

function updateEshmiaChart(models) {
    const ctx = document.getElementById('eshmiaChart');
    if (!ctx) return;

    const labels = models.map(m => formatModelName(m.nome_normalizado));
    const values = models.map(m => m.valor_eshmia || 0);

    // Destroy existing chart
    if (eshmiaChart) {
        eshmiaChart.destroy();
    }

    eshmiaChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'ESHMIA Score',
                data: values,
                backgroundColor: CONFIG.chartColors.gradients,
                borderColor: CONFIG.chartColors.primary,
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 33, 57, 0.95)',
                    titleColor: '#ffffff',
                    bodyColor: '#a0aec0',
                    borderColor: 'rgba(102, 126, 234, 0.5)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function (context) {
                            return `ESHMIA: ${context.parsed.y.toFixed(4)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#a0aec0',
                        font: {
                            family: 'Inter'
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#a0aec0',
                        font: {
                            family: 'Inter'
                        }
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

function updateMetricsChart(models) {
    const ctx = document.getElementById('metricsChart');
    if (!ctx) return;

    const labels = models.map(m => formatModelName(m.nome_normalizado));

    // Extract metrics data
    const ifevalData = models.map(m => m.valores_normalizados?.['IFEval'] || 0);
    const bbhData = models.map(m => m.valores_normalizados?.['BBH'] || 0);
    const mathData = models.map(m => m.valores_normalizados?.['MATH'] || 0);
    const gpqaData = models.map(m => m.valores_normalizados?.['GPQA'] || 0);
    const musrData = models.map(m => m.valores_normalizados?.['MUSR'] || 0);
    const mmluProData = models.map(m => m.valores_normalizados?.['MMLU-PRO'] || 0);

    // Destroy existing chart
    if (metricsChart) {
        metricsChart.destroy();
    }

    metricsChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'IFEval',
                    data: ifevalData,
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    borderColor: '#667eea',
                    pointBackgroundColor: '#667eea',
                    borderWidth: 2
                },
                {
                    label: 'BBH',
                    data: bbhData,
                    backgroundColor: 'rgba(118, 75, 162, 0.2)',
                    borderColor: '#764ba2',
                    pointBackgroundColor: '#764ba2',
                    borderWidth: 2
                },
                {
                    label: 'MATH',
                    data: mathData,
                    backgroundColor: 'rgba(79, 172, 254, 0.2)',
                    borderColor: '#4facfe',
                    pointBackgroundColor: '#4facfe',
                    borderWidth: 2
                },
                {
                    label: 'GPQA',
                    data: gpqaData,
                    backgroundColor: 'rgba(250, 112, 154, 0.2)',
                    borderColor: '#fa709a',
                    pointBackgroundColor: '#fa709a',
                    borderWidth: 2
                },
                {
                    label: 'MUSR',
                    data: musrData,
                    backgroundColor: 'rgba(0, 242, 254, 0.2)',
                    borderColor: '#00f2fe',
                    pointBackgroundColor: '#00f2fe',
                    borderWidth: 2
                },
                {
                    label: 'MMLU-PRO',
                    data: mmluProData,
                    backgroundColor: 'rgba(240, 147, 251, 0.2)',
                    borderColor: '#f093fb',
                    pointBackgroundColor: '#f093fb',
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#a0aec0',
                        font: {
                            family: 'Inter',
                            size: 12
                        },
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 33, 57, 0.95)',
                    titleColor: '#ffffff',
                    bodyColor: '#a0aec0',
                    borderColor: 'rgba(102, 126, 234, 0.5)',
                    borderWidth: 1,
                    padding: 12
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        color: '#a0aec0',
                        font: {
                            family: 'Inter',
                            size: 11
                        }
                    },
                    ticks: {
                        color: '#718096',
                        backdropColor: 'transparent',
                        font: {
                            family: 'Inter'
                        }
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

function updateModelsGrid(data) {
    const grid = document.getElementById('modelsGrid');
    if (!grid || !data.lista_modelos) return;

    // Sort models by ESHMIA
    const sortedModels = [...data.lista_modelos].sort((a, b) =>
        (b.valor_eshmia || 0) - (a.valor_eshmia || 0)
    );

    grid.innerHTML = sortedModels.map((model, index) => {
        const metrics = model.valores_normalizados || {};
        return `
            <div class="model-card fade-in" style="animation-delay: ${index * 0.1}s">
                <div class="model-rank">#${index + 1}</div>
                <h4 class="model-name">${formatModelName(model.nome_normalizado)}</h4>
                <div class="model-eshmia">${(model.valor_eshmia || 0).toFixed(4)}</div>
                <div class="model-metrics">
                    ${Object.entries(metrics).map(([name, value]) => `
                        <div class="metric-row">
                            <span class="metric-name">${name}</span>
                            <span class="metric-value">${value.toFixed(4)}</span>
                        </div>
                        <div class="metric-bar">
                            <div class="metric-fill" style="width: ${Math.min(value * 100, 100)}%"></div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }).join('');
}

function updateLeaderboard(data) {
    const grid = document.getElementById('leaderboardGrid');
    if (!grid || !data.metricas_agregadas) return;

    const metrics = data.metricas_agregadas;
    const metricNames = {
        'IFEval': 'IFEval',
        'BBH': 'BBH',
        'MATH': 'MATH',
        'GPQA': 'GPQA',
        'MUSR': 'MUSR',
        'MMLU-PRO': 'MMLU-PRO'
    };

    grid.innerHTML = Object.entries(metrics).map(([metricKey, metricData]) => {
        const best = formatModelName(metricData.maximo?.modelo || 'N/A');
        const worst = formatModelName(metricData.minimo?.modelo || 'N/A');

        return `
            <div class="leaderboard-card v2 fade-in">
                <div class="leaderboard-header">
                    <span class="metric-chip">${metricNames[metricKey] || metricKey}</span>
                    <p class="leaderboard-subtitle">Melhor e pior desempenho nesta métrica</p>
                </div>
                <div class="leaderboard-body">
                    <div class="leaderboard-row">
                        <span class="leaderboard-label best">🏆 Melhor</span>
                        <span class="leaderboard-model">${best}</span>
                    </div>
                    <div class="leaderboard-row">
                        <span class="leaderboard-label worst">⚠️ Pior</span>
                        <span class="leaderboard-model">${worst}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function updateAnalysis(data) {
    const content = document.getElementById('analysisContent');
    if (!content) return;

    if (data.analise_automatica) {
        content.innerHTML = `<p>${data.analise_automatica}</p>`;
    } else {
        content.innerHTML = '<p class="loading">Análise não disponível</p>';
    }
}

function updateMetricsExplanation(data) {
    if (!data.metricas_agregadas) return;

    const mapping = {
        'IFEval': 'metric-avg-ifeval',
        'BBH': 'metric-avg-bbh',
        'MATH': 'metric-avg-math',
        'GPQA': 'metric-avg-gpqa',
        'MUSR': 'metric-avg-musr',
        'MMLU-PRO': 'metric-avg-mmlu-pro'
    };

    Object.entries(mapping).forEach(([metricName, elementId]) => {
        const el = document.getElementById(elementId);
        if (el && data.metricas_agregadas[metricName]) {
            // Media is 0-1 based on backend calculation logic update
            const val = data.metricas_agregadas[metricName].media || 0;
            // ESHMIA index usually displayed with 4 decimals
            el.textContent = val.toFixed(4);
        }
    });
}

// ===================================
// Connection Status
// ===================================

function updateConnectionStatus(status) {
    const indicator = document.getElementById('connectionStatus');
    const statusText = indicator?.querySelector('.status-text');
    const statusDot = indicator?.querySelector('.status-dot');

    if (!statusText || !statusDot) return;

    switch (status) {
        case 'connected':
            statusText.textContent = 'Conectado';
            statusDot.style.background = '#00f2fe';
            break;
        case 'loading':
            statusText.textContent = 'Atualizando...';
            statusDot.style.background = '#fa709a';
            break;
        case 'error':
            statusText.textContent = 'Erro';
            statusDot.style.background = '#f5576c';
            break;
    }
}

// ===================================
// Loading & Error Handling
// ===================================

function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        if (show) {
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
        }
    }
}

function showError(message) {
    console.error('Error:', message);
    // Could implement a toast notification here
}

// ===================================
// Auto Refresh
// ===================================

// ===================================
// Auto Refresh
// ===================================

function startAutoRefresh() {
    if (autoRefreshTimer) {
        clearInterval(autoRefreshTimer);
    }

    autoRefreshTimer = setInterval(() => {
        console.log('🔄 Auto-refreshing data...');
        loadData(true); // Pass true for silent update
    }, CONFIG.refreshInterval);
}

function stopAutoRefresh() {
    if (autoRefreshTimer) {
        clearInterval(autoRefreshTimer);
        autoRefreshTimer = null;
    }
}

// ===================================
// Utility Functions
// ===================================

function formatModelName(name) {
    if (!name) return 'Unknown';
    return name
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// ===================================
// Cleanup on page unload
// ===================================

window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
    if (eshmiaChart) eshmiaChart.destroy();
    if (metricsChart) metricsChart.destroy();
});
