
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from sqlalchemy.orm import joinedload
from sqlalchemy import func
import datetime
import os

from . import database as db
from .analysis import generate_analysis # Placeholder for now

app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Enable CORS for API access
CORS(app)

# --- Rota para servir o frontend ---
@app.route('/')
def serve_frontend():
    """Serve the main HTML file"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, etc.)"""
    return send_from_directory(app.static_folder, path)

# --- Rota da API (Item 6) ---

@app.route('/api/status')
def get_status():
    """
    Endpoint principal que retorna o estado consolidado do sistema.
    """
    db_session = next(db.get_db())
    try:
        # --- Consulta de Dados ---
        
        # Busca modelos com seus ESHMIA e resultados normalizados
        models_data = db_session.query(db.Modelo).options(
            joinedload(db.Modelo.eshmias),
            joinedload(db.Modelo.resultados).joinedload(db.Resultado.metrica)
        ).all()

        # Calcula o ESHMIA médio do ecossistema (Item 4.4)
        eshmia_medio_result = db_session.query(func.avg(db.Eshmia.valor_eshmia)).scalar()
        eshmia_medio = eshmia_medio_result if eshmia_medio_result is not None else 0

        # Prepara a lista de modelos para o JSON
        modelos_list = []
        for m in models_data:
            if not m.eshmias:  # Apenas inclui modelos com ESHMIA calculado
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

        # --- Métricas Agregadas (para os cards do frontend) ---
        metricas_agregadas = {}
        for metrica_nome in ["IFEval", "BBH", "MATH", "GPQA", "MUSR", "MMLU-PRO"]:
            # Usando subqueries para encontrar o modelo correspondente ao max/min
            
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

        # --- Geração da Análise (Item 8) ---
        # Por enquanto, usamos a função de placeholder
        analise_texto = generate_analysis({
            "modelos": modelos_list,
            "eshmia_medio": eshmia_medio,
            "metricas_agregadas": metricas_agregadas
        })

        # --- Montagem da Resposta JSON (Item 6.2) ---
        response_data = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "lista_modelos": modelos_list,
            "eshmia_medio": eshmia_medio,
            "metricas_agregadas": metricas_agregadas,
            "analise_automatica": analise_texto
        }
        
        return jsonify(response_data)

    finally:
        db_session.close()

if __name__ == '__main__':
    # Este bloco permite executar o servidor Flask para teste
    # python -m backend.app
    app.run(debug=True, port=5001)

