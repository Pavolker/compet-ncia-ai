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
- IFEval: 82.0 (baseline: 100)
- BBH: 75.0 (baseline: 100)
- MATH: 68.0 (baseline: 100)
- GPQA: 55.0 (baseline: 100)
- MUSR: 72.0 (baseline: 100)
- MMLU-PRO: 78.0 (baseline: 100)

Cálculo Normalizado (Valor / 100):
Média (0.82 + 0.75 + 0.68 + 0.55 + 0.72 + 0.78) / 6 = 0.7166
ESHMIA = 0.7166
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

### 2.1 IFEval (Instruction Following Evaluation)
- **Tipo**: Execução de instruções estruturadas
- **Baseline Humano**: 100.0
- **Descrição**: Mede a precisão com que o modelo segue comandos complexos e restrições.

### 2.2 BBH (Big-Bench Hard)
- **Tipo**: Raciocínio lógico multietapas
- **Baseline Humano**: 100.0
- **Descrição**: Desafios que exigem inferência lógica e manipulação de abstrações.

### 2.3 MATH
- **Tipo**: Raciocínio matemático formal
- **Baseline Humano**: 100.0
- **Descrição**: Problemas de matemática de nível olímpico (álgebra, geometria).

### 2.4 GPQA (Graduate-Level Physics Question Answering)
- **Tipo**: Conhecimento científico avançado
- **Baseline Humano**: 100.0
- **Descrição**: Questões de ciência de nível de pós-graduação.

### 2.5 MUSR (Dialogue Reasoning)
- **Tipo**: Coerência em diálogos complexos
- **Baseline Humano**: 100.0
- **Descrição**: Avalia a manutenção de contexto e estrutura argumentativa.

### 2.6 MMLU-PRO (Massive Multitask Language Understanding)
- **Tipo**: Conhecimento profissional multidisciplinar
- **Baseline Humano**: 100.0
- **Descrição**: Versão avançada do MMLU focada em conhecimento técnico e raciocínio.

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
