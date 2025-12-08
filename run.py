#!/usr/bin/env python3
"""
ESHMIA Index Monitor - Orchestration Script
Automates the complete workflow: data collection, calculation, and server startup
"""

import sys
import time
from backend import database as db
from backend import collector
from backend import calculator
from backend.app import app

def print_banner():
    """Print a nice banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           ESHMIA INDEX MONITOR                            ║
    ║           AI Performance Tracking System                  ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def initialize_database():
    """Initialize the database if needed"""
    print("\n📊 Step 1: Checking database...")
    try:
        # Try to connect to existing database
        db_session = next(db.get_db())
        model_count = db_session.query(db.Modelo).count()
        db_session.close()
        
        if model_count == 0:
            print("   ⚠️  Database is empty. Initializing...")
            db.init_db()
            print("   ✅ Database initialized successfully")
        else:
            print(f"   ✅ Database found with {model_count} models")
    except Exception as e:
        print(f"   ⚠️  Database error: {e}")
        print("   🔧 Initializing new database...")
        db.init_db()
        print("   ✅ Database initialized successfully")

def collect_data(use_real: bool = True):
    """Collect data from sources (default: CSV to avoid external instability)."""
    print("\n🔍 Step 2: Collecting data...")
    try:
        db_session = next(db.get_db())
        # Por padrão, carregamos do CSV (use_real=True). Use --mock para usar dados mock.
        collector.collect_and_store_data(db_session, use_real_data=use_real, limit=100)
        db_session.close()
        print("   ✅ Data collection completed")
    except Exception as e:
        print(f"   ❌ Error collecting data: {e}")
        return False
    return True

def calculate_metrics():
    """Calculate normalized metrics and ESHMIA scores"""
    print("\n🧮 Step 3: Calculating metrics...")
    try:
        db_session = next(db.get_db())
        calculator.calculate_and_store_metrics(db_session)
        db_session.close()
        print("   ✅ Metrics calculated successfully")
    except Exception as e:
        print(f"   ❌ Error calculating metrics: {e}")
        return False
    return True

def start_server():
    """Start the Flask server"""
    print("\n🚀 Step 4: Starting web server...")
    print("\n" + "="*60)
    print("   Dashboard available at: http://127.0.0.1:5001")
    print("   API endpoint: http://127.0.0.1:5001/api/status")
    print("="*60 + "\n")
    print("   Press CTRL+C to stop the server\n")
    
    try:
        app.run(debug=False, port=5001, host='127.0.0.1', use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        sys.exit(0)

def main():
    """Main orchestration function"""
    print_banner()
    
    # Check if we should skip data refresh
    skip_refresh = '--skip-refresh' in sys.argv
    
    if not skip_refresh:
        # Step 1: Initialize database
        initialize_database()
        
        # Step 2: Collect data (default: CSV/real). Use --mock para usar dados mock.
        use_real = '--mock' not in sys.argv  # True by default (carrega CSV)
        if not collect_data(use_real=use_real):
            print("\n❌ Data collection failed. Exiting...")
            sys.exit(1)
        
        # Step 3: Calculate metrics
        if not calculate_metrics():
            print("\n❌ Metric calculation failed. Exiting...")
            sys.exit(1)
    else:
        print("\n⏩ Skipping data refresh (--skip-refresh flag detected)")
    
    # Step 4: Start server
    start_server()

if __name__ == '__main__':
    main()
