#!/usr/bin/env python3
"""
Coletor de Dados - Carrega dados prioritariamente do PostgreSQL (Docker)
"""

import os
import datetime
import pandas as pd
from sqlalchemy.orm import Session
from . import database as db
from .postgres_collector import PostgresCollector, convert_postgres_row_to_model_data

def get_mock_data():
    """Fallback mock data"""
    return [
        {
            "nome": "Atlas-5", 
            "fonte": "SimTheory", 
            "metricas": {"IFEval": 80.0, "BBH": 75.0, "MATH": 90.0, "GPQA": 70.0, "MUSR": 65.0, "MMLU-PRO": 88.0},
            "url_origem": "https://example.com/models/atlas-5"
        }
    ]

def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

CSV_FILE = "big_benchmarks_top100.csv"

def load_csv_data(filepath: str = CSV_FILE) -> list:
    """
    Carrega dados do arquivo CSV como fallback.
    """
    if not os.path.exists(filepath):
        print(f"⚠️ Arquivo CSV {filepath} não encontrado.")
        return []
    
    try:
        print(f"📂 Carregando dados do CSV: {filepath}")
        df = pd.read_csv(filepath)
        model_list = []
        for _, row in df.iterrows():
            model_list.append({
                "nome": str(row.get("model", "Unknown")),
                "fonte": "Open LLM Leaderboard (CSV)",
                "metricas": {
                    "IFEval": safe_float(row.get("ifeval", 0)),
                    "BBH": safe_float(row.get("bbh", 0)),
                    "MATH": safe_float(row.get("math", 0)),
                    "GPQA": safe_float(row.get("gpqa", 0)),
                    "MUSR": safe_float(row.get("musr", 0)),
                    "MMLU-PRO": safe_float(row.get("mmlu_pro", 0))
                },
                "url_origem": "https://huggingface.co/spaces/open-llm-leaderboard"
            })
        return model_list
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        return []

def collect_and_store_data(db_session: Session, use_real_data: bool = True, limit: int = 150):
    """
    Carrega dados do PostgreSQL Docker, CSV ou Mock e armazena no eshmia_db local.
    """
    print(f"\n🔍 Iniciando coleta de dados (Modo: {'Real' if use_real_data else 'Mock'})...")
    
    model_list = []
    required_metrics = ["IFEval", "BBH", "MATH", "GPQA", "MUSR", "MMLU-PRO"]
    
    # 1. Tenta Postgres se solicitado
    if use_real_data:
        pg_collector = PostgresCollector()
        if pg_collector.connect():
            pg_data = pg_collector.get_latest_data(limit=limit)
            for row in pg_data:
                try:
                    model_data = convert_postgres_row_to_model_data(row)
                    if any(metric in model_data.get('metricas', {}) for metric in required_metrics):
                        model_list.append(model_data)
                except Exception as e:
                    print(f"⚠️ Erro ao converter linha do Postgres: {e}")
                    continue
            pg_collector.disconnect()
    
    # 2. Tenta CSV como fallback secundário se model_list estiver vazio e use_real_data for True
    if not model_list and use_real_data:
        print("⚠️ Falha na conexão com Postgres. Tentando carregar do CSV...")
        model_list = load_csv_data()
        if model_list:
            model_list = model_list[:limit]
    
    # 3. Tenta Mock como último recurso
    if not model_list:
        print(f"⚠️ {'Nenhum dado encontrado em Postgres/CSV' if use_real_data else 'Usando dados Mock por solicitação'}. Usando Mock...")
        model_list = get_mock_data()

    print(f"📦 Processando {len(model_list)} modelos para o banco de dados ESHMIA...")

    # Garante que as métricas existem no banco ESHMIA
    for m_nome in required_metrics:
        if not db_session.query(db.Metrica).filter(db.Metrica.nome == m_nome).first():
            db_session.add(db.Metrica(nome=m_nome, baseline_humano=100.0, fonte_baseline='Human Baseline'))
    db_session.commit()

    metricas_db = {m.nome: m for m in db_session.query(db.Metrica).all()}
    
    models_added = 0
    results_added = 0
    
    for model_data in model_list:
        model_name = model_data.get("nome", "Unknown")
        model_metrics = model_data.get("metricas", {})
        
        normalized_name = model_name.lower().replace(" ", "-").replace("/", "-")
        existing = db_session.query(db.Modelo).filter(
            db.Modelo.nome_normalizado == normalized_name
        ).first()
        
        if existing:
            modelo = existing
        else:
            modelo = db.Modelo(
                nome_normalizado=normalized_name,
                fonte=model_data.get("fonte", "Postgres Docker"),
                url_origem=model_data.get("url_origem", "")
            )
            db_session.add(modelo)
            db_session.flush()
            models_added += 1
        
        for metrica_nome, valor in model_metrics.items():
            if metrica_nome in metricas_db:
                res_existente = db_session.query(db.Resultado).filter(
                    db.Resultado.modelo_id == modelo.id,
                    db.Resultado.metrica_id == metricas_db[metrica_nome].id
                ).first()
                
                if not res_existente:
                    resultado = db.Resultado(
                        modelo_id=modelo.id,
                        metrica_id=metricas_db[metrica_nome].id,
                        valor_cru=valor, 
                        valor_normalizado=valor / 100.0 
                    )
                    db_session.add(resultado)
                    results_added += 1
    
    db_session.commit()
    print(f"✅ Sincronização de dados finalizada: {models_added} novos modelos, {results_added} novos resultados.")

def get_real_data(limit: int = 100):
    pg_collector = PostgresCollector()
    if pg_collector.connect():
        data = pg_collector.get_latest_data(limit=limit)
        pg_collector.disconnect()
        return [convert_postgres_row_to_model_data(row) for row in data]
    return get_mock_data()
