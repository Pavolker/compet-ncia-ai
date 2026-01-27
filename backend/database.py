import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# --- Configuração do Banco de Dados ---
DB_TYPE = os.getenv('DB_TYPE', 'postgresql')

if DB_TYPE == 'postgresql':
    POSTGRES_HOST = os.getenv('POSTGRES_HOST')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT')
    POSTGRES_DB = os.getenv('POSTGRES_DB')
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    
    if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB]):
        raise ValueError("Faltam variáveis de ambiente para conexão com PostgreSQL (verifique .env)")

    # Desativa SSL para conexões localhost/Docker
    is_localhost = POSTGRES_HOST in ['localhost', '127.0.0.1', '0.0.0.0']
    ssl_mode = 'disable' if is_localhost else 'require'
    
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}?sslmode={ssl_mode}"
else:
    DATABASE_URL = "sqlite:///project.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Definição das Tabelas ---
class Modelo(Base):
    __tablename__ = 'modelos'
    id = Column(Integer, primary_key=True, index=True)
    nome_normalizado = Column(String, unique=True, nullable=False)
    fonte = Column(String, nullable=True)
    url_origem = Column(String, nullable=True)
    data_coleta = Column(DateTime, server_default=func.now())
    resultados = relationship("Resultado", back_populates="modelo")
    eshmias = relationship("Eshmia", back_populates="modelo")

class Metrica(Base):
    __tablename__ = 'metricas'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, nullable=False)
    baseline_humano = Column(Float, nullable=False)
    fonte_baseline = Column(String, nullable=True)
    resultados = relationship("Resultado", back_populates="metrica")

class Resultado(Base):
    __tablename__ = 'resultados'
    id = Column(Integer, primary_key=True, index=True)
    modelo_id = Column(Integer, ForeignKey('modelos.id'), nullable=False)
    metrica_id = Column(Integer, ForeignKey('metricas.id'), nullable=False)
    valor_cru = Column(Float, nullable=False)
    valor_normalizado = Column(Float, nullable=True)
    data_coleta = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    link_origem = Column(String, nullable=True)
    modelo = relationship("Modelo", back_populates="resultados")
    metrica = relationship("Metrica", back_populates="resultados")

class Eshmia(Base):
    __tablename__ = 'eshmia'
    id = Column(Integer, primary_key=True, index=True)
    modelo_id = Column(Integer, ForeignKey('modelos.id'), nullable=False)
    valor_eshmia = Column(Float, nullable=False)
    data_calculo = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    modelo = relationship("Modelo", back_populates="eshmias")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(Metrica).first():
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
    db.close()

if __name__ == '__main__':
    init_db()
