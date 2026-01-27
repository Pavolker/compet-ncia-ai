#!/usr/bin/env python3
"""
PostgreSQL Data Collector - Fetches benchmark data from PostgreSQL database
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime


class PostgresCollector:
    """Handles PostgreSQL connections and data fetching"""
    
    def __init__(self):
        """Initialize PostgreSQL connection parameters from environment variables"""
        self.host = os.getenv('POSTGRES_HOST')
        self.port = os.getenv('POSTGRES_PORT')
        self.database = os.getenv('SOURCE_DB') or os.getenv('POSTGRES_DB')
        self.user = os.getenv('POSTGRES_USER')
        self.password = os.getenv('POSTGRES_PASSWORD')
        self.connection = None
    
    def connect(self):
        """Establish connection to PostgreSQL database"""
        try:
            is_localhost = self.host in ['localhost', '127.0.0.1', '0.0.0.0']
            ssl_mode = 'disable' if is_localhost else 'require'
            
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                sslmode=ssl_mode
            )
            print(f"✅ Connected to source PostgreSQL database ({self.database}) successfully")
            return True
        except psycopg2.Error as e:
            print(f"❌ PostgreSQL connection error to {self.database}: {e}")
            return False
    
    def disconnect(self):
        """Close PostgreSQL connection"""
        if self.connection:
            self.connection.close()
            print("✅ PostgreSQL connection closed")
    
    def get_latest_data(self, limit: int = 200):
        """
        Fetch the most recent benchmark data records
        """
        if not self.connection:
            print("❌ Not connected to PostgreSQL")
            return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Busca os últimos N registros, independente do batch, ordenados por data
                query = """
                    SELECT * FROM benchmark_data 
                    ORDER BY created_at DESC
                    LIMIT %s
                """
                cursor.execute(query, (limit,))
                rows = cursor.fetchall()
                print(f"✅ Fetched {len(rows)} records from PostgreSQL ({self.database})")
                return [dict(row) for row in rows]
        
        except psycopg2.Error as e:
            print(f"❌ Query error: {e}")
            return []

def convert_postgres_row_to_model_data(row: dict) -> dict:
    """
    Convert PostgreSQL benchmark_data row to model data format
    """
    def safe_float(value):
        try:
            if value is None or value == '-' or value == 'N/A':
                return None
            return float(value)
        except (ValueError, TypeError):
            return None
    
    metrics = {}
    metric_columns = {
        'if_eval': 'IFEval',
        'bbh': 'BBH',
        'math': 'MATH',
        'gpqa': 'GPQA',
        'musr': 'MUSR',
        'mmlu_pro': 'MMLU-PRO'
    }
    
    for pg_col, metric_name in metric_columns.items():
        value = safe_float(row.get(pg_col))
        if value is not None:
            metrics[metric_name] = value
    
    return {
        'nome': row.get('model', 'Unknown'),
        'tipo': row.get('type', 'Unknown'),
        'rank': row.get('rank', 0),
        'fonte': 'PostgreSQL Benchmark Database',
        'metricas': metrics,
        'url_origem': 'postgresql://benchmark_data',
        'co2_cost': row.get('co2_cost', 'N/A'),
        'average': row.get('average')
    }
