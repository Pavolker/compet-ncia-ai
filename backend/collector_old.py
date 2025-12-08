
import os
import datetime
import pandas as pd
from sqlalchemy.orm import Session
from . import database as db

# ===================================
# COLETOR DE DADOS - NOVO BACKEND
# ===================================

CSV_FILE = "big_benchmarks_top100.csv"

def load_csv_data(filepath: str = CSV_FILE) -> pd.DataFrame:
    """
    Carrega dados do arquivo CSV do Open LLM Leaderboard.
    
    Args:
        filepath: Caminho do arquivo CSV
        
    Returns:
        DataFrame com os dados
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo {filepath} não encontrado")
    
    print(f"📂 Carregando dados do CSV: {filepath}")
    df = pd.read_csv(filepath)
    print(f"✅ {len(df)} registros carregados do CSV")
    return df

def get_mock_data():
    """
    Retorna dados de exemplo para teste (fallback).
    Usado como fallback quando o CSV não está disponível.
    """
    print("📦 Usando dados MOCK (fallback)")
    return [
        {
            "nome": "Atlas-5", 
            "fonte": "SimTheory", 
            "metricas": {"MMLU": 0.91, "RE-Bench": 0.96, "HAR": 1.0},
            "url_origem": "https://example.com/models/atlas-5"
        },
        {
            "nome": "Prometheus-Pro", 
            "fonte": "EdenAI", 
            "metricas": {"MMLU": 0.95, "RE-Bench": 0.92, "HAR": 1.0},
            "url_origem": "https://example.com/models/prometheus-pro"
        },
        {
            "nome": "Orion-X", 
            "fonte": "Artificial Analysis", 
            "metricas": {"MMLU": 0.88, "RE-Bench": 0.98, "HAR": 0.9},
            "url_origem": "https://example.com/models/orion-x"
        },
        {
            "nome": "Nexus-9", 
            "fonte": "HuggingFace", 
            "metricas": {"MMLU": 0.85, "RE-Bench": 0.89, "HAR": 1.05},
            "url_origem": "https://example.com/models/nexus-9"
        },
    ]

def collect_and_store_data(db_session: Session, use_real_data: bool = False, limit: int = 100):
    """
    Carrega dados do CSV (ou mock) e armazena no banco de dados.
    
    Args:
        db_session: Sessão SQLAlchemy
        use_real_data: Se True, carrega do CSV; se False, usa mock
        limit: Número máximo de registros a processar
    """
    print("\n🔍 Coletando dados...")
    
    # Tenta carregar do CSV primeiro
    if use_real_data:
        try:
            df = load_csv_data(CSV_FILE)
            model_list = []
            for idx, row in df.head(limit).iterrows():
                model_list.append({
                    "nome": row.get("model", f"Model_{idx}"),
                    "fonte": f"Open LLM Leaderboard ({row.get('type', 'unknown')})",
                    "metricas": {
                        "MMLU": float(row.get("ifeval", 0)) / 100.0,
                        "RE-Bench": float(row.get("bbh", 0)) / 100.0,
                        "HAR": float(row.get("math", 0)) / 100.0,
                    },
                    "url_origem": "https://huggingface.co/spaces/open-llm-leaderboard"
                })
        except Exception as e:
            print(f"⚠️  Erro ao carregar CSV: {e}")
            print("Usando dados MOCK...")
            model_list = get_mock_data()
    else:
        model_list = get_mock_data()
    
    # Armazena no banco
    metricas_db = {m.nome: m for m in db_session.query(db.Metrica).all()}
    required_metrics = {"MMLU", "RE-Bench", "HAR"}
    
    models_added = 0
    results_added = 0
    
    for model_data in model_list:
        model_name = model_data.get("nome", "Unknown")
        model_metrics = model_data.get("metricas", {})
        
        # Valida se tem as métricas necessárias
        if not required_metrics.issubset(model_metrics.keys()):
            print(f"  ⏭️  Modelo '{model_name}' ignorado (métricas incompletas)")
            continue
        
        # Verifica se já existe
        existing = db_session.query(db.Modelo).filter(
            db.Modelo.nome_normalizado == model_name.lower().replace(" ", "-")
        ).first()
        
        if existing:
            print(f"  ♻️  Modelo '{model_name}' já existe")
            continue
        
        # Cria novo modelo
        modelo = db.Modelo(
            nome_normalizado=model_name.lower().replace(" ", "-"),
            fonte=model_data.get("fonte", "Unknown"),
            url_origem=model_data.get("url_origem", "")
        )
        db_session.add(modelo)
        db_session.flush()
        models_added += 1
        
        # Adiciona resultados
        for metrica_nome, valor in model_metrics.items():
            if metrica_nome in metricas_db:
                resultado = db.Resultado(
                    modelo_id=modelo.id,
                    metrica_id=metricas_db[metrica_nome].id,
                    valor_cru=valor * 100,  # Denormaliza
                    valor_normalizado=valor
                )
                db_session.add(resultado)
                results_added += 1
    
    db_session.commit()
    print(f"✅ Coleta concluída: {models_added} modelos, {results_added} resultados")

def get_real_data(limit: int = 100):
    """
    Obtém dados do CSV ou mock (compatível com interface anterior).
    
    Args:
        limit: Número máximo de registros
        
    Returns:
        Lista de dicionários com dados dos modelos
    """
    try:
        df = load_csv_data(CSV_FILE)
        models = []
        for idx, row in df.head(limit).iterrows():
            models.append({
                "nome": row.get("model", f"Model_{idx}"),
                "tipo": row.get("type", "unknown"),
                "rank": row.get("rank", idx + 1),
                "metricas": {
                    "MMLU": float(row.get("ifeval", 0)) / 100.0,
                    "RE-Bench": float(row.get("bbh", 0)) / 100.0,
                    "HAR": float(row.get("math", 0)) / 100.0,
                }
            })
        return models
    except Exception as e:
        print(f"⚠️  Erro ao buscar CSV: {e}, usando mock...")
        return get_mock_data()



def get_mock_data():
    """
    Retorna uma lista de dados mockados para simular a coleta.
    Usado como fallback quando a API real falha.
    """
    print("📦 Usando dados MOCK (fallback)")
    return [
        {
            "nome": "Atlas-5", 
            "fonte": "SimTheory", 
            "metricas": {"MMLU": 0.91, "RE-Bench": 0.96, "HAR": 1.1},
            "url_origem": "https://example.com/models/atlas-5"
        },
        {
            "nome": "Prometheus-Pro", 
            "fonte": "EdenAI", 
            "metricas": {"MMLU": 0.95, "RE-Bench": 0.92, "HAR": 1.2},
            "url_origem": "https://example.com/models/prometheus-pro"
        },
        {
            "nome": "Orion-X", 
            "fonte": "Artificial Analysis", 
            "metricas": {"MMLU": 0.88, "RE-Bench": 0.98, "HAR": 0.9},
            "url_origem": "https://example.com/models/orion-x"
        },
        {
            "nome": "Nexus-9", 
            "fonte": "HuggingFace", 
            "metricas": {"MMLU": 0.85, "RE-Bench": 0.89, "HAR": 1.05},
            "url_origem": "https://example.com/models/nexus-9"
        },
    ]

# ===================================
# FUNÇÕES PRINCIPAIS
# ===================================

def normalize_model_name(name: str) -> str:
    """Padroniza o nome do modelo."""
    # Remove caracteres especiais e espaços extras
    normalized = name.strip()
    # Mantém apenas os primeiros 50 caracteres para evitar nomes muito longos
    if len(normalized) > 50:
        normalized = normalized[:50]
    return normalized.lower().replace(" ", "-").replace("/", "-")

def collect_and_store_data(db_session: Session, use_real_data=USE_REAL_DATA, limit=20):
    """
    Busca dados (reais ou mockados), filtra e armazena no banco de dados.
    
    Args:
        db_session: Sessão do banco de dados
        use_real_data: Se True, busca dados reais; se False, usa mock
        limit: Número máximo de modelos para coletar
    """
    print("\n" + "="*60)
    print("🚀 INICIANDO COLETA DE DADOS")
    print("="*60)
    
    # Decide qual fonte de dados usar
    if use_real_data:
        print("📡 Modo: COLETA REAL (HuggingFace API)")
        model_data_list = get_real_data(limit)
    else:
        print("📦 Modo: DADOS MOCK")
        model_data_list = get_mock_data()
    
    # Busca os objetos de métrica do banco para associar aos resultados
    metricas_db = {m.nome: m for m in db_session.query(db.Metrica).all()}
    required_metrics = {"MMLU", "RE-Bench", "HAR"}
    
    models_added = 0
    models_skipped = 0
    
    for model_data in model_data_list:
        model_metrics = model_data.get("metricas", {})
        
        # --- Regra de Filtragem ---
        # Se o modelo não tiver as três métricas, ele é ignorado.
        if not required_metrics.issubset(model_metrics.keys()):
            models_skipped += 1
            print(f"⏭️  Modelo '{model_data['nome']}' ignorado (métricas incompletas)")
            continue

        # --- Armazenamento do Modelo ---
        nome_normalizado = normalize_model_name(model_data["nome"])
        
        # Verifica se o modelo já existe
        modelo = db_session.query(db.Modelo).filter_by(nome_normalizado=nome_normalizado).first()
        if not modelo:
            modelo = db.Modelo(
                nome_normalizado=nome_normalizado,
                fonte=model_data.get("fonte", "Unknown"),
                url_origem=model_data.get("url_origem", f"https://example.com/models/{nome_normalizado}")
            )
            db_session.add(modelo)
            db_session.flush()  # Para obter o ID do modelo
            models_added += 1
            print(f"✅ Modelo '{model_data['nome']}' adicionado")
        else:
            print(f"♻️  Modelo '{model_data['nome']}' já existe, atualizando métricas")
        
        # --- Armazenamento dos Resultados ---
        for metrica_nome, valor in model_metrics.items():
            if metrica_nome in metricas_db:
                # Remove resultado antigo se existir
                db_session.query(db.Resultado).filter_by(
                    modelo_id=modelo.id,
                    metrica_id=metricas_db[metrica_nome].id
                ).delete()
                
                # Adiciona novo resultado
                resultado = db.Resultado(
                    modelo_id=modelo.id,
                    metrica_id=metricas_db[metrica_nome].id,
                    valor_cru=valor,
                    data_coleta=datetime.datetime.utcnow(),
                    link_origem=model_data.get("url_origem", "")
                )
                db_session.add(resultado)

    db_session.commit()
    
    print("\n" + "="*60)
    print("✅ COLETA CONCLUÍDA")
    print(f"   • Modelos adicionados: {models_added}")
    print(f"   • Modelos ignorados: {models_skipped}")
    print(f"   • Total processado: {len(model_data_list)}")
    print("="*60 + "\n")

if __name__ == '__main__':
    # Bloco para testar o coletor de forma isolada
    print("🧪 TESTANDO O COLETOR DE DADOS\n")
    db_session = next(db.get_db())
    try:
        # Limpa dados antigos para um teste limpo
        print("🗑️  Limpando dados antigos...")
        db_session.query(db.Resultado).delete()
        db_session.query(db.Eshmia).delete()
        db_session.query(db.Modelo).delete()
        db_session.commit()
        
        # Coleta dados
        collect_and_store_data(db_session, use_real_data=True, limit=15)
        
        # Verifica se os dados foram inseridos
        model_count = db_session.query(db.Modelo).count()
        result_count = db_session.query(db.Resultado).count()
        print(f"\n📊 Resultado do teste:")
        print(f"   • {model_count} modelos no banco")
        print(f"   • {result_count} resultados no banco")

    finally:
        db_session.close()

