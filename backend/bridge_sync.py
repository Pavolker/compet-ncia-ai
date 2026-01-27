import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório atual ao sys.path para importações locais
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, Base, SessionLocal
from backend.collector import collect_and_store_data
from backend.calculator import calculate_and_store_metrics

def run_sync():
    print("🔄 Iniciando sincronização do ESHMIA com o banco de dados Docker...")
    
    # 1. Garantir que as tabelas existem no eshmia_db
    print("📦 Inicializando tabelas no eshmia_db...")
    Base.metadata.create_all(bind=engine)
    
    # Criar uma sessão do banco
    db_session = SessionLocal()
    
    try:
        # 2. Coletar dados do benchmark_db e salvar no eshmia_db
        print("📥 Coletando dados do benchmark_db (Postgres Docker)...")
        collect_and_store_data(db_session)
        
        # 3. Calcular o índice ESHMIA para os novos dados
        print("🧮 Calculando índice ESHMIA...")
        calculate_and_store_metrics(db_session)
        
        print("✅ Sincronização e cálculo concluídos com sucesso.")
    except Exception as e:
        print(f"❌ Erro durante a sincronização: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_session.close()

    print("✨ Processo de ponte concluído!")

if __name__ == "__main__":
    run_sync()
