# ESHMIA Index - Especificação Técnica

## 1. Conceito do Índice ESHMIA

### 1.1 Definição
**ESHMIA** (Ensemble Score of Human-relative Model Intelligence and Alignment) é um índice composto que mede a performance de modelos de IA em relação ao desempenho humano em múltiplas métricas de benchmark.

### 1.2 Objetivo
Fornecer uma métrica única e normalizada que permita:
- Comparação direta entre diferentes modelos de IA
- Avaliação da evolução do ecossistema de IA ao longo do tempo
- Identificação de modelos que superam o baseline humano

### 1.3 Fórmula de Cálculo

```
ESHMIA = (Σ métricas_normalizadas) / n_métricas

onde:
métrica_normalizada = valor_cru_modelo / baseline_humano
```

**Exemplo:**
```
Modelo X:
- MMLU: 0.92 (baseline humano: 0.89)
- RE-Bench: 0.98 (baseline humano: 0.95)
- HAR: 1.15 (baseline humano: 1.0)

MMLU_norm = 0.92 / 0.89 = 1.0337
RE-Bench_norm = 0.98 / 0.95 = 1.0316
HAR_norm = 1.15 / 1.0 = 1.15

ESHMIA = (1.0337 + 1.0316 + 1.15) / 3 = 1.0718
```

### 1.4 Interpretação

| ESHMIA | Interpretação |
|--------|---------------|
| < 0.8 | Significativamente abaixo do baseline humano |
| 0.8 - 0.95 | Abaixo do baseline humano |
| 0.95 - 1.05 | Próximo ao baseline humano |
| 1.05 - 1.2 | Acima do baseline humano |
| > 1.2 | Significativamente acima do baseline humano |

## 2. Métricas Componentes

### 2.1 MMLU (Massive Multitask Language Understanding)
- **Tipo**: Conhecimento geral e raciocínio
- **Baseline Humano**: 0.89 (89%)
- **Fonte**: [MMLU Paper](https://arxiv.org/abs/2009.03300)
- **Descrição**: Avalia conhecimento em 57 disciplinas acadêmicas

### 2.2 RE-Bench (Reasoning Evaluation Benchmark)
- **Tipo**: Raciocínio lógico e resolução de problemas
- **Baseline Humano**: 0.95 (95%)
- **Fonte**: Benchmark customizado
- **Descrição**: Testa capacidade de raciocínio complexo

### 2.3 HAR (Human Alignment Rating)
- **Tipo**: Alinhamento com valores humanos
- **Baseline Humano**: 1.0 (100%)
- **Fonte**: Avaliação customizada
- **Descrição**: Mede alinhamento ético e segurança

## 3. Arquitetura do Sistema

### 3.1 Fluxo de Dados

```
┌─────────────┐
│   Scraper   │ ──┐
│  (Futuro)   │   │
└─────────────┘   │
                  ▼
┌─────────────┐   ┌──────────────┐   ┌─────────────┐
│  Collector  │──▶│   Database   │──▶│ Calculator  │
│   (Mock)    │   │   (SQLite)   │   │ (Normalize) │
└─────────────┘   └──────────────┘   └─────────────┘
                         │                    │
                         ▼                    ▼
                  ┌──────────────┐   ┌─────────────┐
                  │  Flask API   │◀──│   ESHMIA    │
                  └──────────────┘   │   Scores    │
                         │           └─────────────┘
                         ▼
                  ┌──────────────┐
                  │   Frontend   │
                  │  Dashboard   │
                  └──────────────┘
```

### 3.2 Schema do Banco de Dados

```sql
-- Tabela de Modelos
CREATE TABLE modelos (
    id INTEGER PRIMARY KEY,
    nome_normalizado TEXT UNIQUE NOT NULL,
    fonte TEXT,
    url_origem TEXT,
    data_coleta DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Métricas
CREATE TABLE metricas (
    id INTEGER PRIMARY KEY,
    nome TEXT UNIQUE NOT NULL,
    baseline_humano REAL NOT NULL,
    fonte_baseline TEXT
);

-- Tabela de Resultados
CREATE TABLE resultados (
    id INTEGER PRIMARY KEY,
    modelo_id INTEGER REFERENCES modelos(id),
    metrica_id INTEGER REFERENCES metricas(id),
    valor_cru REAL NOT NULL,
    valor_normalizado REAL,
    data_coleta DATETIME DEFAULT CURRENT_TIMESTAMP,
    link_origem TEXT
);

-- Tabela ESHMIA
CREATE TABLE eshmia (
    id INTEGER PRIMARY KEY,
    modelo_id INTEGER REFERENCES modelos(id),
    valor_eshmia REAL NOT NULL,
    data_calculo DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 4. API REST

### 4.1 Endpoints

#### GET /api/status

**Descrição**: Retorna o estado consolidado do sistema

**Response**:
```json
{
  "timestamp": "ISO-8601 datetime",
  "eshmia_medio": float,
  "lista_modelos": [
    {
      "nome_normalizado": string,
      "valor_eshmia": float,
      "valores_normalizados": {
        "MMLU": float,
        "RE-Bench": float,
        "HAR": float
      }
    }
  ],
  "metricas_agregadas": {
    "MMLU": {
      "maximo": {"modelo": string},
      "minimo": {"modelo": string}
    },
    "RE-Bench": {...},
    "HAR": {...}
  },
  "analise_automatica": string
}
```

**Status Codes**:
- 200: Sucesso
- 500: Erro interno do servidor

## 5. Frontend

### 5.1 Componentes

1. **Hero Stats**: Cards com estatísticas principais
2. **Charts**: Visualizações interativas (Chart.js)
3. **Models Grid**: Ranking de modelos
4. **Leaderboard**: Líderes por métrica
5. **Analysis**: Análise textual automática

### 5.2 Design System

**Cores Principais**:
- Primary: `#667eea` (Roxo)
- Secondary: `#764ba2` (Roxo escuro)
- Success: `#4facfe` (Azul)
- Warning: `#fa709a` (Rosa)

**Tipografia**:
- Headings: Inter (700-800)
- Body: Inter (400-500)
- Code: JetBrains Mono (400-600)

**Efeitos**:
- Glassmorphism: `backdrop-filter: blur(20px)`
- Gradientes: Linear gradients em 135deg
- Animações: Smooth transitions (250ms ease)

## 6. Melhorias Futuras

### 6.1 Fase 2: Coleta Real
- Implementar scraper para LMSYS Chatbot Arena
- Adicionar suporte para HuggingFace Leaderboard
- Integração com Papers with Code

### 6.2 Fase 3: Análise Avançada
- Histórico temporal de ESHMIA
- Predição de tendências
- Comparação de categorias (open-source vs proprietário)

### 6.3 Fase 4: Produção
- Deploy em servidor cloud
- Sistema de cache (Redis)
- Autenticação e rate limiting
- Monitoramento e alertas

## 7. Referências

- [MMLU Paper](https://arxiv.org/abs/2009.03300)
- [LMSYS Chatbot Arena](https://chat.lmsys.org/)
- [HuggingFace Leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)
- [Papers with Code](https://paperswithcode.com/)

---

**Versão**: 1.0  
**Data**: Dezembro 2025  
**Autor**: ESHMIA Index Monitor Team
