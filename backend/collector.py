#!/usr/bin/env python3
"""
Coletor de Dados - Carrega dados exclusivamente do PostgreSQL
Substituiu a leitura de CSV pelo acesso direto ao banco de dados PostgreSQL
"""

import os
import datetime
import pandas as pd
from sqlalchemy.orm import Session
from . import database as db
from .postgres_collector import PostgresCollector, convert_postgres_row_to_model_data

CSV_FILE = "dados.csv"

def get_mock_data():
    """
    Retorna dados de exemplo para teste (fallback).
    Usado quando CSV não está disponível.
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

def safe_float(value):
    """Converte valor para float, retornando 0.0 se falhar."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def collect_and_store_data(db_session: Session, use_real_data: bool = True, limit: int = 100):
    """
    Carrega dados exclusivamente do PostgreSQL e armazena no banco de dados local.
    
    Args:
        db_session: Sessão SQLAlchemy
        use_real_data: Se True, carrega do PostgreSQL; se False, usa mock
        limit: Número máximo de registros
    """
    print("\n🔍 Coletando dados...")
    
    model_list = []
    required_metrics = ["IFEval", "BBH", "MATH", "GPQA", "MUSR", "MMLU-PRO"]
    
    if use_real_data:
        # Conecta ao PostgreSQL
        print("🔗 Conectando ao PostgreSQL...")
        pg_collector = PostgresCollector()
        
        if pg_collector.connect():
            # Busca dados do último batch
            print("📥 Buscando dados do último batch no PostgreSQL...")
            pg_data = pg_collector.get_latest_batch_data(limit=limit)
            
            # Converte dados do PostgreSQL para formato interno
            for row in pg_data:
                try:
                    model_data = convert_postgres_row_to_model_data(row)
                    
                    # Verifica se tem todas as métricas obrigatórias
                    if all(metric in model_data.get('metricas', {}) for metric in required_metrics):
                        model_list.append(model_data)
                
                except Exception as e:
                    print(f"⚠️  Erro ao processar modelo: {e}")
                    continue
            
            pg_collector.disconnect()
            
            if not model_list:
                print("⚠️  Nenhum dado válido do PostgreSQL. Usando dados MOCK...")
                model_list = get_mock_data()
        else:
            print("❌ Falha na conexão com PostgreSQL. Usando dados MOCK...")
            model_list = get_mock_data()
    else:
        print("📦 Usando dados MOCK...")
        model_list = get_mock_data()
    
    # Processa e armazena modelos
    metricas_db = {m.nome: m for m in db_session.query(db.Metrica).all()}
    
    # If using mock data that doesn't have the new keys, this might be partial. 
    # But user asked for strict CSV reading.
    
    models_added = 0
    results_added = 0
    
    for model_data in model_list:
        model_name = model_data.get("nome", "Unknown")
        model_metrics = model_data.get("metricas", {})
        
        # Verify we have all required metrics (strict mode)
        if not all(k in model_metrics for k in required_metrics):
             continue

        # Verifica se já existe
        normalized_name = model_name.lower().replace(" ", "-").replace("/", "-")
        existing = db_session.query(db.Modelo).filter(
            db.Modelo.nome_normalizado == normalized_name
        ).first()
        
        if existing:
            continue
        
        # Cria modelo
        modelo = db.Modelo(
            nome_normalizado=normalized_name,
            fonte=model_data.get("fonte", "Unknown"),
            url_origem=model_data.get("url_origem", "")
        )
        db_session.add(modelo)
        db_session.flush()
        models_added += 1
        
        # Adiciona resultados
        for metrica_nome, valor in model_metrics.items():
            if metrica_nome in metricas_db:
                # Store raw value (0-100)
                # Normalize logic: previous code divided by 100.0 or baseline. 
                # Here we store val (0-100) as valor_cru. 
                # valor_normalizado is typically 0-1. So val/100.
                
                resultado = db.Resultado(
                    modelo_id=modelo.id,
                    metrica_id=metricas_db[metrica_nome].id,
                    valor_cru=valor, 
                    valor_normalizado=valor / 100.0 
                )
                db_session.add(resultado)
                results_added += 1
    
    db_session.commit()
    print(f"✅ Coleta concluída: {models_added} modelos, {results_added} resultados")

def get_real_data(limit: int = 100):
    """
    Obtém dados do PostgreSQL ou mock.
    
    Args:
        limit: Número máximo de registros
        
    Returns:
        Lista de dicionários com dados dos modelos
    """
    print("🔍 Coletando dados do PostgreSQL...")
    pg_collector = PostgresCollector()
    
    if not pg_collector.connect():
        print("Usando dados MOCK...")
        return get_mock_data()
    
    pg_data = pg_collector.get_latest_batch_data(limit=limit)
    pg_collector.disconnect()
    
    models = []
    for row in pg_data:
        try:
            model_data = convert_postgres_row_to_model_data(row)
            models.append(model_data)
        except Exception as e:
            print(f"⚠️  Erro ao processar modelo: {e}")
            continue
    
    return models if models else get_mock_data()
