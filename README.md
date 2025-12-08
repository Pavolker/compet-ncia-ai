# ESHMIA Index Monitor

## 1. Visão Geral do Projeto

Este projeto, **ESHMIA Index Monitor**, é um aplicativo full-stack projetado para rastrear, analisar e visualizar automaticamente o desempenho de modelos de Inteligência Artificial com base em um índice personalizado chamado ESHMIA (Ensemble Score of Human-relative Model Intelligence and Alignment).

O sistema foi projetado para operar de forma totalmente autônoma:
- Coleta periodicamente uma lista de modelos de IA e seus benchmarks.
- Armazena os dados em um banco de dados local (SQLite).
- Normaliza as métricas e calcula o índice ESHMIA.
- Expõe uma API RESTful com os dados processados.
- Apresenta um dashboard web interativo com gráficos e análises.

**Estado Atual:** ✅ **PROJETO COMPLETO E FUNCIONAL**
- Backend Flask totalmente implementado e testado
- Frontend moderno com design premium (glassmorphism, gradientes, animações)
- Dashboard interativo com Chart.js
- API REST funcionando perfeitamente
- Script de orquestração automática (`run.py`)

## 2. Estrutura do Projeto

```
/
├── backend/
│   ├── app.py             # Servidor Flask e API endpoint
│   ├── calculator.py      # Lógica de cálculo (Normalização e ESHMIA)
│   ├── collector.py       # Coletor de dados (atualmente com dados mock)
│   ├── database.py        # Definição do schema do BD com SQLAlchemy
│   ├── analysis.py        # Geração de análise textual
│   └── requirements.txt   # Dependências do Python
├── frontend/
│   ├── index.html         # Dashboard principal
│   ├── style.css          # Design moderno com glassmorphism
│   └── script.js          # Lógica de apresentação + Chart.js
├── run.py                 # Script de orquestração automática
└── project.db             # Arquivo do banco de dados SQLite
```

## 3. Início Rápido

### Método 1: Usando o Script de Orquestração (Recomendado)

```bash
# Instalar dependências
pip install -r backend/requirements.txt

# Executar o sistema completo (inicializa DB, coleta dados mock, calcula métricas e inicia servidor)
python3 run.py

# Tentar coleta real (pode falhar se a API do HuggingFace estiver instável)
python3 run.py --real-data
```

O dashboard estará disponível em: **http://127.0.0.1:5001**

### Método 2: Execução Manual Passo a Passo

#### Passo 1: Instalar Dependências

```bash
pip install -r backend/requirements.txt
```

#### Passo 2: Inicializar o Banco de Dados

```bash
python3 backend/database.py
```

#### Passo 3: Popular o Banco de Dados com Dados Mock

```bash
python3 -m backend.collector
```

#### Passo 4: Executar os Cálculos

```bash
python3 -m backend.calculator
```

#### Passo 5: Iniciar o Servidor

```bash
python3 -m backend.app
```

Acesse o dashboard em: **http://127.0.0.1:5001**

## 4. Funcionalidades do Dashboard

### 📊 Estatísticas em Tempo Real
- **ESHMIA Médio**: Índice médio do ecossistema de IA
- **Modelos Ativos**: Quantidade de modelos em monitoramento
- **Métricas**: MMLU, RE-Bench, HAR
- **Última Atualização**: Timestamp da última coleta

### 📈 Visualizações Interativas
- **Gráfico de Barras**: Comparação de ESHMIA entre modelos
- **Gráfico Radar**: Distribuição de métricas normalizadas
- **Atualização Automática**: Refresh a cada 30 segundos

### 🏆 Ranking e Análises
- **Ranking de Modelos**: Ordenado por índice ESHMIA
- **Líderes por Métrica**: Melhores performances individuais
- **Análise Automática**: Insights gerados pelo sistema

## 5. API REST

### Endpoint Principal

**GET** `/api/status`

Retorna o estado consolidado do sistema:

```json
{
  "timestamp": "2025-12-08T11:46:49.884731",
  "eshmia_medio": 1.0193,
  "lista_modelos": [
    {
      "nome_normalizado": "prometheus-pro",
      "valor_eshmia": 1.0786,
      "valores_normalizados": {
        "HAR": 1.2,
        "MMLU": 1.0674,
        "RE-Bench": 0.9684
      }
    }
  ],
  "metricas_agregadas": { ... },
  "analise_automatica": "..."
}
```

## 6. Tecnologias Utilizadas

### Backend
- **Python 3**
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **SQLite** - Database
- **Flask-CORS** - Cross-origin support

### Frontend
- **HTML5** - Estrutura semântica
- **CSS3** - Design moderno com glassmorphism
- **JavaScript (Vanilla)** - Lógica de apresentação
- **Chart.js** - Visualizações interativas
- **Google Fonts** - Inter & JetBrains Mono

## 7. Próximos Passos (Melhorias Futuras)

### Prioridade Alta
1. **Scraper Real**: Substituir dados mock por coleta real de benchmarks
2. **Mais Métricas**: Adicionar HumanEval, GSM8K, etc.
3. **Histórico**: Armazenar e visualizar evolução temporal

### Prioridade Média
4. **Autenticação**: Sistema de login (se necessário)
5. **Exportação**: Download de dados em CSV/JSON
6. **Notificações**: Alertas de mudanças significativas

### Prioridade Baixa
7. **Deploy**: Configuração para produção (Gunicorn, Nginx)
8. **Testes**: Suite de testes automatizados
9. **Documentação**: API docs com Swagger/OpenAPI

## 8. Desenvolvimento

### Estrutura de Dados

**Fórmula ESHMIA:**
```
ESHMIA = (MMLU_norm + RE-Bench_norm + HAR_norm) / 3
onde X_norm = valor_cru / baseline_humano
```

**Baselines Humanos:**
- MMLU: 0.89
- RE-Bench: 0.95
- HAR: 1.0

### Comandos Úteis

```bash
# Apenas iniciar servidor (sem refresh de dados)
python3 run.py --skip-refresh

# Reinicializar banco de dados
python3 backend/database.py

# Testar cálculos
python3 -m backend.calculator

# Verificar API
curl http://127.0.0.1:5001/api/status
```

## 9. Licença e Créditos

Desenvolvido como sistema de monitoramento de IA.
© 2025 ESHMIA Index Monitor
