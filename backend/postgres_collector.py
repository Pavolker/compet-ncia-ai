#!/usr/bin/env python3
"""
PostgreSQL Data Collector - Fetches benchmark data from PostgreSQL database
Replaces CSV-based data collection with direct database queries
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime


class PostgresCollector:
    """Handles PostgreSQL connections and data fetching"""
    
    def __init__(self):
        """Initialize PostgreSQL connection parameters"""
        self.host = os.getenv('POSTGRES_HOST', 'centerbeam.proxy.rlwy.net')
        self.port = os.getenv('POSTGRES_PORT', '16594')
        self.database = os.getenv('POSTGRES_DB', 'railway')
        self.user = os.getenv('POSTGRES_USER', 'postgres')
        self.password = os.getenv('POSTGRES_PASSWORD', 'kSYfUUXCRhOPVPwztXwieXmYOGnmSlZD')
        self.connection = None
    
    def connect(self):
        """Establish connection to PostgreSQL database with SSL"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                sslmode='require'
            )
            print("✅ Connected to PostgreSQL database successfully")
            return True
        except psycopg2.Error as e:
            print(f"❌ PostgreSQL connection error: {e}")
            return False
    
    def disconnect(self):
        """Close PostgreSQL connection"""
        if self.connection:
            self.connection.close()
            print("✅ PostgreSQL connection closed")
    
    def get_latest_batch_data(self, limit: int = 100):
        """
        Fetch benchmark data from the latest batch
        
        Args:
            limit: Maximum number of records to fetch
        
        Returns:
            List of dictionaries with model data
        """
        if not self.connection:
            print("❌ Not connected to PostgreSQL")
            return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT * FROM benchmark_data 
                    WHERE batch_id = (
                        SELECT batch_id FROM benchmark_batches 
                        ORDER BY created_at DESC LIMIT 1
                    )
                    ORDER BY rank
                    LIMIT %s
                """
                cursor.execute(query, (limit,))
                rows = cursor.fetchall()
                print(f"✅ Fetched {len(rows)} records from PostgreSQL")
                return [dict(row) for row in rows]
        
        except psycopg2.Error as e:
            print(f"❌ Query error: {e}")
            return []
    
    def get_batch_data(self, batch_id: str, limit: int = 100):
        """
        Fetch benchmark data from a specific batch
        
        Args:
            batch_id: Identifier of the batch
            limit: Maximum number of records to fetch
        
        Returns:
            List of dictionaries with model data
        """
        if not self.connection:
            print("❌ Not connected to PostgreSQL")
            return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT * FROM benchmark_data 
                    WHERE batch_id = %s
                    ORDER BY rank
                    LIMIT %s
                """
                cursor.execute(query, (batch_id, limit))
                rows = cursor.fetchall()
                print(f"✅ Fetched {len(rows)} records from batch {batch_id}")
                return [dict(row) for row in rows]
        
        except psycopg2.Error as e:
            print(f"❌ Query error: {e}")
            return []
    
    def get_all_batches(self):
        """
        Fetch list of all available batches
        
        Returns:
            List of dictionaries with batch metadata
        """
        if not self.connection:
            print("❌ Not connected to PostgreSQL")
            return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT batch_id, created_at, sources 
                    FROM benchmark_batches 
                    ORDER BY created_at DESC
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                print(f"✅ Found {len(rows)} batches in PostgreSQL")
                return [dict(row) for row in rows]
        
        except psycopg2.Error as e:
            print(f"❌ Query error: {e}")
            return []


def convert_postgres_row_to_model_data(row: dict) -> dict:
    """
    Convert PostgreSQL benchmark_data row to model data format
    
    Args:
        row: Dictionary from PostgreSQL benchmark_data table
    
    Returns:
        Dictionary with model data format
    """
    def safe_float(value):
        """Safely convert value to float"""
        try:
            if value is None or value == '-' or value == 'N/A':
                return None
            return float(value)
        except (ValueError, TypeError):
            return None
    
    # Map PostgreSQL columns to metric names
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


if __name__ == '__main__':
    # Test the PostgreSQL collector
    print("Testing PostgreSQL Collector...\n")
    
    collector = PostgresCollector()
    if collector.connect():
        # Fetch latest batch
        data = collector.get_latest_batch_data(limit=5)
        print(f"\nSample data (first 5 records):")
        for row in data:
            print(f"  - {row.get('model')}: {row.get('average')}")
        
        # Fetch available batches
        batches = collector.get_all_batches()
        if batches:
            print(f"\nAvailable batches (latest 3):")
            for batch in batches[:3]:
                print(f"  - {batch.get('batch_id')}: {batch.get('created_at')}")
        
        collector.disconnect()
    else:
        print("Failed to connect to PostgreSQL database")
