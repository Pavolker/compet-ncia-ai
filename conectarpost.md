informações Técnicas para Acesso ao Banco de Dados

1. Credenciais de Conexão PostgreSQL:
plaintext
Host: centerbeam.proxy.rlwy.net
Port: 16594
Database: railway
Username: postgres
Password: kSYfUUXCRhOPVPwztXwieXmYOGnmSlZD


Connection String completa:

plaintext
postgresql://postgres:kSYfUUXCRhOPVPwztXwieXmYOGnmSlZD@centerbeam.proxy.rlwy.net:16594/railway

SSL: Obrigatório (use sslmode=require ou ssl: { rejectUnauthorized: false })

2. Estrutura das Tabelas:

Tabela: benchmark_batches

Armazena metadata de cada execução:

Coluna	Tipo	Descrição
id	SERIAL (PK)	ID auto-incremento
batch_id	VARCHAR(50) UNIQUE	Identificador único do lote
created_at	TIMESTAMP	Data/hora da execução
sources	TEXT[]	Array de URLs fontes

Tabela: benchmark_data

Armazena os dados dos modelos:

Coluna	Tipo	Descrição

id	SERIAL (PK)	ID auto-incremento
batch_id	VARCHAR(50) (FK)	Referência ao batch
rank	INTEGER	Posição no ranking
type	VARCHAR(50)	Tipo do modelo
model	VARCHAR(200)	Nome do modelo
average	VARCHAR(20)	Média geral
if_eval	VARCHAR(20)	Score IFEval
bbh	VARCHAR(20)	Score BBH
math	VARCHAR(20)	Score MATH
gpqa	VARCHAR(20)	Score GPQA
musr	VARCHAR(20)	Score MUSR
mmlu_pro	VARCHAR(20)	Score MMLU-PRO
co2_cost	VARCHAR(50)	Custo de CO2
created_at	TIMESTAMP	Data/hora do registro

3. Consultas SQL Úteis:

Buscar dados do último batch:

sql
SELECT * FROM benchmark_data 
WHERE batch_id = (
  SELECT batch_id FROM benchmark_batches 
  ORDER BY created_at DESC LIMIT 1
)
ORDER BY rank;

Buscar todos os batches disponíveis:

sql
SELECT batch_id, created_at, sources 
FROM benchmark_batches 
ORDER BY created_at DESC;

Buscar dados de um batch específico:
sql
SELECT * FROM benchmark_data 
WHERE batch_id = 'batch_2025-12-18T13-12-45-123Z'
ORDER BY rank;

Comparar top 10 entre dois batches:
sql
SELECT b1.model, b1.average as batch1_avg, b2.average as batch2_avg
FROM benchmark_data b1
JOIN benchmark_data b2 ON b1.model = b2.model
WHERE b1.batch_id = 'batch_id_1' 
  AND b2.batch_id = 'batch_id_2'
  AND b1.rank <= 10
ORDER BY b1.rank;


4. Exemplo de Conexão (Node.js/TypeScript):

typescript
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: 'postgresql://postgres:kSYfUUXCRhOPVPwztXwieXmYOGnmSlZD@centerbeam.proxy.rlwy.net:16594/railway',
  ssl: {
    rejectUnauthorized: false
  }
});

// Buscar último batch
const result = await pool.query(`
  SELECT * FROM benchmark_data 
  WHERE batch_id = (
    SELECT batch_id FROM benchmark_batches 
    ORDER BY created_at DESC LIMIT 1
  )
  ORDER BY rank
`);

console.log(result.rows);

5. Índices Disponíveis:
idx_batch_id - Índice em benchmark_data.batch_id (melhora performance de filtros por batch)
idx_created_at - Índice em benchmark_data.created_at (melhora ordenação temporal)
