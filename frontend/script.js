// ===================================
// ESHMIA Index Monitor - JavaScript
// Dashboard Logic & API Integration
// ===================================

// Configuration
const CONFIG = {
    apiUrl: '/api/status', 
    staticDataUrl: 'data.json', // Fallback for static deployment
    refreshInterval: 30000, 
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

        let data;
        try {
            // Tenta primeiro a API dinâmica (Flask)
            const response = await fetch(CONFIG.apiUrl);
            if (!response.ok) throw new Error('API offline');
            data = await response.json();
            console.log('📊 Data loaded from API');
        } catch (apiError) {
            console.log('⚠️ API offline, trying static data.json...');
            // Fallback para o arquivo estático gerado no build
            const response = await fetch(CONFIG.staticDataUrl);
            if (!response.ok) {
                throw new Error(`Static data not found! status: ${response.status}`);
            }
            data = await response.json();
            console.log('📊 Data loaded from static data.json');
        }

        if (!data) throw new Error('No data available');

        // Update all sections
        updateHeroStats(data);
        updateProgressChart(data);
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

function updateProgressChart(data) {
    const fill = document.getElementById('eshmiaProgressFill');
    const indicator = document.getElementById('eshmiaProgressIndicator');
    const valueLabel = document.getElementById('eshmiaProgressValue');

    if (fill && indicator && valueLabel && data.eshmia_medio !== undefined) {
        let value = data.eshmia_medio;

        // Clamp value for visual representation (0 to 1)
        // If it goes beyond 1, we max it out at 100% physically but show real number
        let percentage = Math.min(Math.max(value, 0), 1) * 100;

        // Update DOM
        fill.style.width = `${percentage}%`;
        indicator.style.left = `${percentage}%`;

        // Format value
        valueLabel.textContent = typeof value === 'number' ? value.toFixed(4) : value;

        // Visual feedback based on value
        if (value >= 1.0) {
            valueLabel.style.color = '#00f2fe'; // Cyan / Superhuman
            valueLabel.style.textShadow = '0 0 10px rgba(0, 242, 254, 0.5)';
        } else {
            valueLabel.style.color = '#f093fb'; // Pink / Human-below
            valueLabel.style.textShadow = 'none';
        }
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

    // Filter top 20 for charts
    const topModels = sortedModels.slice(0, 20);

    updateEshmiaChart(topModels);
    updateMetricsChart(topModels);
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

    // Limit to top 10
    const topModels = sortedModels.slice(0, 10);

    grid.innerHTML = topModels.map((model, index) => {
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

// ===================================
// Book Sidebar & Modal Logic
// ===================================

document.addEventListener('DOMContentLoaded', () => {
    // Sidebar Elements
    const sidebar = document.getElementById('bookSidebar');
    const toggleBtn = document.getElementById('sidebarToggle');
    const closeSidebarBtn = document.getElementById('closeSidebar');

    // Modal Elements
    const modal = document.getElementById('readingModal');
    const closeModalBtn = document.getElementById('closeModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    // Cards
    const cards = document.querySelectorAll('.thesis-card');

    // Content Data
    const thesisContent = {
        1: {
            title: "Nosso Livro",
            text: "Este livro introduz uma estrutura analítica para compreender a relação entre competências humanas e sistemas de inteligência artificial. A partir do conceito de Zona de Desenvolvimento Proximal, de Lev Vygotsky, propõe-se um modelo de medição da distância entre o desempenho individual e o desempenho alcançado quando mediado por IA. Essa distância é formalizada no índice ESHMIA, construído a partir de seis benchmarks internacionais que avaliam execução, raciocínio, cálculo, ciência, diálogo e conhecimento.<br><br>O livro organiza as bases teóricas, descreve os instrumentos de medição e apresenta a lógica de acompanhamento contínuo da aproximação entre humanos e modelos de IA. Não se trata de projeções sobre substituição, mas da análise de como ferramentas algorítmicas ampliam capacidades em tarefas específicas. Ao integrar dados atualizados, referenciais de pesquisa e uma estrutura conceitual clara, a obra oferece ao leitor um quadro consistente para interpretar o avanço da IA e suas implicações para o trabalho cognitivo humano."
        },
        2: {
            title: "A Nossa Base: Vygotsky",
            text: "Lev Vygotsky investigou como o desenvolvimento humano ocorre por meio da mediação cultural. A ideia central é que as capacidades individuais não emergem de forma isolada, mas do uso compartilhado de ferramentas simbólicas construídas historicamente. Entre aquilo que uma pessoa já executa de modo autônomo e aquilo que só realiza com apoio existe a Zona de Desenvolvimento Proximal (ZDP). A travessia dessa zona depende de mediações externas — pessoas, artefatos e sistemas de representação.<br><br>Ferramentas culturais transformam a forma de pensar: não apenas ampliam habilidades existentes, mas reorganizam processos internos. A escrita altera a memória; os números reconfiguram a percepção de quantidade; a linguagem formal redefine categorias de análise. Esse mecanismo de mediação fornece um modelo para compreender como novas tecnologias, incluindo sistemas de IA, podem modificar o modo como pessoas executam tarefas cognitivas."
        },
        3: {
            title: "A ZDP - IA",
            text: "A ZDP-AI aplica o conceito de Vygotsky a interações entre humanos e sistemas algorítmicos. Ela descreve um intervalo mensurável entre dois níveis: o repertório cognitivo que o usuário possui sem auxílio e o desempenho que atinge quando utiliza uma IA como mediadora. A ZDP-AI não expressa carência, mas um espaço funcional em que a intervenção tecnológica altera a capacidade efetiva de resolução de tarefas.<br><br>Quanto maior a diferença entre o nível autônomo e o nível assistido, maior a margem de transformação possível. A ZDP-AI permite quantificar esse intervalo, produzindo um referencial para compreender ganhos obtidos por meio da colaboração com sistemas de IA."
        },
        4: {
            title: "O Que a ZDP-AI Revela",
            text: "A ZDP-AI introduz três elementos analíticos:<br><br>1. <strong>Aplicação em adultos.</strong> A ZDP deixa de ser instrumento para descrever desenvolvimento infantil e passa a ser uma métrica de ampliação de competências já estabelecidas em usuários adultos.<br>2. <strong>Superioridade circunscrita.</strong> Sistemas de IA apresentam desempenho superior apenas em domínios específicos, mensuráveis e limitados. O foco desloca-se de generalizações amplas para competências claramente definidas.<br>3. <strong>Relação pessoa–ferramenta.</strong> O modelo não replica a dinâmica pedagógica tradicional, mas mantém a estrutura essencial: existe uma distância operacional entre dois estados de desempenho que pode ser reduzida por mediação tecnológica."
        },
        5: {
            title: "As Seis Competências Humanas",
            text: "A comparação entre humanos e IA opera sobre seis domínios com métricas consolidadas na literatura de avaliação de modelos:<br><br>• <strong>Execução</strong> — capacidade de seguir instruções estruturadas.<br>• <strong>Raciocínio</strong> — resolução de problemas multietapas.<br>• <strong>Cálculo</strong> — manipulação matemática formal.<br>• <strong>Ciência</strong> — aplicação de conhecimento técnico-especializado.<br>• <strong>Diálogo</strong> — coerência em sequências conversacionais.<br>• <strong>Conhecimento</strong> — recuperação e organização de informações factuais.<br><br>Esses domínios são adequados para mensuração padronizada e permitem estabelecer comparações diretas. Áreas fora desses contornos — como deliberação ética, interpretação situada ou processos criativos não recombinantes — não se prestam ao mesmo tipo de mensuração comparativa."
        },
        6: {
            title: "Como Se Mede a IA",
            text: "O desempenho de sistemas de IA é avaliado por bancos de testes padronizados que permitem comparação objetiva entre modelos. Cada benchmark aborda uma competência específica e foi desenvolvido por grupos de pesquisa reconhecidos internacionalmente.<br><br>• <strong>IFEval</strong> — Instruction Following Evaluation<br>Avalia a execução de instruções estruturadas, medindo a precisão com que o modelo segue comandos complexos.<br><br>• <strong>BBH</strong> — Big-Bench Hard<br>Conjunto de problemas de raciocínio multietapas que exige inferência lógica, composição e manipulação de abstrações.<br><br>• <strong>MATH</strong> — Mathematics Benchmark<br>Banco de problemas matemáticos formais, incluindo álgebra, geometria e combinatória, com verificação objetiva de acertos.<br><br>• <strong>GPQA</strong> — Graduate-Level Physics Question Answering<br>Conjunto de questões de física em nível de pós-graduação, orientado à avaliação de raciocínio científico especializado.<br><br>• <strong>MUSR</strong> — Multi-Step Unified Structured Reasoning (Dialogue Benchmark)<br>Avalia a coerência conversacional em múltiplas etapas, integrando referência contextual e manutenção de estrutura argumentativa.<br><br>• <strong>MMLU-PRO</strong> — Massive Multitask Language Understanding – Professional<br>Teste de conhecimento factual e profissional em diversos domínios, com questões de nível universitário e técnico.<br><br>Esses benchmarks formam um conjunto padronizado para comparar desempenhos, acompanhar evolução temporal dos modelos e observar a distância relativa entre respostas humanas e respostas algorítmicas."
        },
        7: {
            title: "O Que É o Índice ESHMIA",
            text: "O índice ESHMIA (Eficiência de Superação Humana por Modelo de Inteligência Artificial) expressa a relação entre desempenho humano e desempenho de IA nas seis métricas. Para cada domínio, estabelece-se uma razão entre o resultado obtido pelo modelo e o resultado humano de referência. A média dessas seis razões compõe o índice agregado.<br><br>Faixas interpretativas:<br>• < 1.0 — desempenho inferior ao humano na média dos testes.<br>• = 1.0 — paridade de desempenho.<br>• > 1.0 — desempenho proporcionalmente superior.<br><br>O ESHMIA não se refere a atributos gerais de capacidade humana, mas apenas à quantificação do intervalo mensurável em tarefas padronizadas."
        },
        8: {
            title: "O Projeto Centauro",
            text: "O caso Kasparov–Deep Blue demonstrou que sistemas computacionais podem superar humanos em tarefas delimitadas, mas também revelou que combinações híbridas humano–máquina podem produzir resultados superiores aos dois componentes isolados. A ideia do “centauro” surge como metáfora operacional para descrever configurações colaborativas nas quais humanos contribuem com direção estratégica, interpretação contextual e gestão de objetivos, enquanto máquinas executam cálculos, análises e operações de alta velocidade.<br><br>O Projeto Centauro adota essa lógica como estrutura para interação colaborativa: humanos definem finalidades e critérios; sistemas de IA processam tarefas que dependem de escala, precisão ou velocidade. A soma não é fusão de identidades, mas composição funcional."
        },
        9: {
            title: "IA: Potencializadora",
            text: "A ZDP-AI desloca o foco da comparação direta entre humanos e IA para a medição do que se torna possível quando ambos operam em conjunto. A função da IA, nesse enquadramento, é reorganizar o esforço cognitivo: externaliza etapas de cálculo, síntese ou busca, permitindo que o usuário concentre recursos em atividades que requerem interpretação, elaboração estratégica ou integração de múltiplos contextos.<br><br>A colaboração não substitui competências humanas; reorganiza a sua distribuição ao longo de um processo. Tarefas que exigem análise situada, formulação de critérios e integração de valores permanecem sob responsabilidade humana."
        },
        10: {
            title: "Os Limites da IA",
            text: "Modelos de IA são sistemas estatísticos treinados sobre grandes conjuntos de dados. Não possuem interioridade, autoconsciência, intenção ou experiência própria. Suas respostas resultam de padrões aprendidos, não de vivências ou deliberações subjetivas.<br><br>Permanece fora do escopo técnico atual:<br><br>• Processos criativos que envolvem ruptura não derivada de dados prévios.<br>• Sabedoria prática orientada por situações singulares.<br>• Julgamento ético dependente de responsabilidade pessoal.<br>• Empatia como reconhecimento de alteridade.<br>• Presença incorporada orientada por experiência sensório-motora.<br><br>O mapeamento desses limites delimita condições adequadas de uso e define fronteiras para a delegação de tarefas a sistemas de IA."
        }
    };

    // Toggle Sidebar
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    if (closeSidebarBtn && sidebar) {
        closeSidebarBtn.addEventListener('click', () => {
            sidebar.classList.remove('open');
        });
    }

    // Close sidebar when clicking outside
    document.addEventListener('click', (e) => {
        if (sidebar && sidebar.classList.contains('open') &&
            !sidebar.contains(e.target) &&
            !toggleBtn.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });

    // Open Modal on Card Click
    cards.forEach(card => {
        card.addEventListener('click', () => {
            const id = card.getAttribute('data-id');
            const content = thesisContent[id];

            if (content) {
                modalTitle.textContent = content.title;
                modalBody.innerHTML = `<p>${content.text}</p>`;
                modal.classList.add('open');

                // Close sidebar on mobile/desktop appropriately if needed? 
                // Currently keeping it open logic.
            }
        });
    });

    // Close Modal
    if (closeModalBtn && modal) {
        closeModalBtn.addEventListener('click', () => {
            modal.classList.remove('open');
        });
    }

    // Close modal on backlight click
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('open');
            }
        });
    }
});
