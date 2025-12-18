
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
import datetime

# --- Configuração do Banco de Dados ---
# Use PostgreSQL se disponível, caso contrário fallback para SQLite
DB_TYPE = os.getenv('DB_TYPE', 'postgresql')

if DB_TYPE == 'postgresql':
    # PostgreSQL Configuration
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'centerbeam.proxy.rlwy.net')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '16594')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'railway')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'kSYfUUXCRhOPVPwztXwieXmYOGnmSlZD')
    
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}?sslmode=require"
else:
    # SQLite Fallback
    DATABASE_URL = "sqlite:///project.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Definição das Tabelas (Modelos ORM) ---

class Modelo(Base):
    """Tabela para armazenar os modelos de IA coletados."""
    __tablename__ = 'modelos'
    id = Column(Integer, primary_key=True, index=True)
    nome_normalizado = Column(String, unique=True, nullable=False)
    fonte = Column(String, nullable=True)
    url_origem = Column(String, nullable=True)
    data_coleta = Column(DateTime, server_default=func.now())
    
    resultados = relationship("Resultado", back_populates="modelo")
    eshmias = relationship("Eshmia", back_populates="modelo")

class Metrica(Base):
    """Tabela para definir as métricas e seus baselines humanos."""
    __tablename__ = 'metricas'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, nullable=False)
    baseline_humano = Column(Float, nullable=False)
    fonte_baseline = Column(String, nullable=True)

    resultados = relationship("Resultado", back_populates="metrica")

class Resultado(Base):
    """Tabela para armazenar os resultados brutos e normalizados das métricas para cada modelo."""
    __tablename__ = 'resultados'
    id = Column(Integer, primary_key=True, index=True)
    modelo_id = Column(Integer, ForeignKey('modelos.id'), nullable=False)
    metrica_id = Column(Integer, ForeignKey('metricas.id'), nullable=False)
    valor_cru = Column(Float, nullable=False)
    valor_normalizado = Column(Float, nullable=True)
    data_coleta = Column(DateTime, default=datetime.datetime.utcnow)
    link_origem = Column(String, nullable=True)

    modelo = relationship("Modelo", back_populates="resultados")
    metrica = relationship("Metrica", back_populates="resultados")

class Eshmia(Base):
    """Tabela para armazenar o índice ESHMIA calculado para cada modelo."""
    __tablename__ = 'eshmia'
    id = Column(Integer, primary_key=True, index=True)
    modelo_id = Column(Integer, ForeignKey('modelos.id'), nullable=False)
    valor_eshmia = Column(Float, nullable=False)
    data_calculo = Column(DateTime, default=datetime.datetime.utcnow)
    
    modelo = relationship("Modelo", back_populates="eshmias")

# --- Funções de Utilitário do Banco de Dados ---

def get_db():
    """Retorna uma nova sessão do banco de dados."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Inicializa o banco de dados. Cria todas as tabelas e popula com dados iniciais
    (métricas e baselines).
    """
    # Para SQLite, apaga o banco de dados antigo se existir
    if DB_TYPE != 'postgresql' and os.path.exists('project.db'):
        os.remove('project.db')

    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Verifica se as métricas já existem (evita duplicatas em PostgreSQL)
    existing_metrics = db.query(Metrica).first()
    if existing_metrics:
        print("✅ Métricas já existem no banco de dados.")
        db.close()
        return
    
    # Popula a tabela de métricas com os baselines humanos
    metricas_iniciais = [
        Metrica(nome='IFEval', baseline_humano=100.0, fonte_baseline='Human Baseline'),
        Metrica(nome='BBH', baseline_humano=100.0, fonte_baseline='Human Baseline'),
        Metrica(nome='MATH', baseline_humano=100.0, fonte_baseline='Human Baseline'),
        Metrica(nome='GPQA', baseline_humano=100.0, fonte_baseline='Human Baseline'),
        Metrica(nome='MUSR', baseline_humano=100.0, fonte_baseline='Human Baseline'),
        Metrica(nome='MMLU-PRO', baseline_humano=100.0, fonte_baseline='Human Baseline')
    ]
    
    db.add_all(metricas_iniciais)
    db.commit()
    
    print("✅ Banco de dados inicializado com sucesso e métricas populadas.")
    
    db.close()

if __name__ == '__main__':
    # Este bloco permite executar `python backend/database.py` para inicializar o banco.
    print("Inicializando o banco de dados...")
    init_db()

