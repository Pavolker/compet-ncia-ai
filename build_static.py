
import json
import datetime
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from backend import database as db
from backend.analysis import generate_analysis

from backend import collector
from backend import calculator

# Configuração do caminho de saída
OUTPUT_FILE = "frontend/data.json"

def build_static_data():
    """
    Gera um arquivo estático JSON com os dados do dashboard,
    permitindo deploy como site estático no Netlify.
    """
    print("🚀 Iniciando build estático...")
    
    # Inicializa DB (garante que está tudo correto)
    print("📦 Inicializando banco de dados...")
    db.init_db()
    
    db_session = next(db.get_db())
    try:
        # Coleta os dados do CSV para o banco (CRÍTICO para deploy onde o banco começa vazio)
        print("📥 Populando banco de dados a partir do CSV...")
        collector.collect_and_store_data(db_session, use_real_data=True)
        
        # Calcula métricas (ESSENCIAL para gerar os ESHMIAs)
        print("🧮 Calculando métricas e ESHMIA...")
        calculator.calculate_and_store_metrics(db_session)
        
        print("📊 Consultando banco de dados...")
        
        # --- Consulta de Dados (Cópia da lógica do app.py) ---
        
        # Busca modelos com seus ESHMIA e resultados normalizados
        models_data = db_session.query(db.Modelo).options(
            joinedload(db.Modelo.eshmias),
            joinedload(db.Modelo.resultados).joinedload(db.Resultado.metrica)
        ).all()

        # Calcula o ESHMIA médio do ecossistema
        eshmia_medio_result = db_session.query(func.avg(db.Eshmia.valor_eshmia)).scalar()
        eshmia_medio = eshmia_medio_result if eshmia_medio_result is not None else 0

        # Prepara a lista de modelos para o JSON
        modelos_list = []
        for m in models_data:
            if not m.eshmias:  
                continue
            
            model_info = {
                "nome_normalizado": m.nome_normalizado,
                "valor_eshmia": m.eshmias[0].valor_eshmia if m.eshmias else None,
                "valores_normalizados": {
                    res.metrica.nome: res.valor_normalizado 
                    for res in m.resultados if res.valor_normalizado is not None
                }
            }
            modelos_list.append(model_info)

        # --- Métricas Agregadas ---
        metricas_agregadas = {}
        for metrica_nome in ["IFEval", "BBH", "MATH", "GPQA", "MUSR", "MMLU-PRO"]:
            # Subquery para valor máximo
            max_subquery = db_session.query(func.max(db.Resultado.valor_normalizado)).join(db.Metrica).filter(db.Metrica.nome == metrica_nome).scalar_subquery()
            max_model_query = db_session.query(db.Modelo.nome_normalizado).join(db.Resultado).join(db.Metrica).filter(
                db.Metrica.nome == metrica_nome,
                db.Resultado.valor_normalizado == max_subquery
            ).first()

            # Subquery para valor mínimo
            min_subquery = db_session.query(func.min(db.Resultado.valor_normalizado)).join(db.Metrica).filter(db.Metrica.nome == metrica_nome).scalar_subquery()
            min_model_query = db_session.query(db.Modelo.nome_normalizado).join(db.Resultado).join(db.Metrica).filter(
                db.Metrica.nome == metrica_nome,
                db.Resultado.valor_normalizado == min_subquery
            ).first()

            # Cálculo da média da métrica
            avg_val = db_session.query(func.avg(db.Resultado.valor_normalizado)).join(db.Metrica).filter(db.Metrica.nome == metrica_nome).scalar()

            metricas_agregadas[metrica_nome] = {
                "maximo": {"modelo": max_model_query[0] if max_model_query else "N/A"},
                "minimo": {"modelo": min_model_query[0] if min_model_query else "N/A"},
                "media": avg_val if avg_val is not None else 0
            }

        # --- Geração da Análise ---
        analise_texto = generate_analysis({
            "modelos": modelos_list,
            "eshmia_medio": eshmia_medio
        })

        # --- Montagem do Payload Final ---
        response_data = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "lista_modelos": modelos_list,
            "eshmia_medio": eshmia_medio,
            "metricas_agregadas": metricas_agregadas,
            "analise_automatica": analise_texto
        }
        
        # --- Salvar em JSON ---
        print(f"💾 Salvando em {OUTPUT_FILE}...")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, ensure_ascii=False, indent=2)
            
        print("✅ Build estático concluído com sucesso!")
        
    finally:
        db_session.close()

if __name__ == "__main__":
    build_static_data()
