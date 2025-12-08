
from sqlalchemy.orm import Session, joinedload
from . import database as db
import datetime

def calculate_and_store_metrics(db_session: Session):
    """
    Calcula os valores normalizados e o ESHMIA para os modelos no banco.
    """
    print("Iniciando cálculo de métricas normalizadas e ESHMIA...")

    # Limpa os cálculos antigos para evitar duplicatas
    db_session.query(db.Eshmia).delete()
    db_session.query(db.Resultado).filter(db.Resultado.valor_normalizado != None).update({"valor_normalizado": None})
    db_session.commit()

    # Busca todos os modelos com seus resultados e métricas associadas
    models = db_session.query(db.Modelo).options(
        joinedload(db.Modelo.resultados).joinedload(db.Resultado.metrica)
    ).all()

    for modelo in models:
        if not modelo.resultados:
            continue

        # --- Normalização (Item 4.1) ---
        normalized_scores = {}
        raw_scores = {}
        
        for resultado in modelo.resultados:
            if resultado.metrica.baseline_humano > 0:
                # Normalizado é 0-1 (dado baseline=100 e cru=0-100)
                valor_normalizado = resultado.valor_cru / resultado.metrica.baseline_humano
                resultado.valor_normalizado = valor_normalizado
                normalized_scores[resultado.metrica.nome] = valor_normalizado
                raw_scores[resultado.metrica.nome] = resultado.valor_cru

        # --- Cálculo do ESHMIA (Item 4.3) ---
        required_metrics = {"IFEval", "BBH", "MATH", "GPQA", "MUSR", "MMLU-PRO"}
        
        if required_metrics.issubset(normalized_scores.keys()):
            # ESHMIA = média simples dos 6 indicadores NORMALIZADOS (0-1)
            # Como o baseline é 100, e os dados são 0-100, isso resulta em 0-1.
            # 1.0 = Nível Humano (100 pontos em todas as métricas)
            eshmia_value = sum(normalized_scores[metrica] for metrica in required_metrics) / len(required_metrics)
            
            # --- Armazenamento do ESHMIA (Item 4.5) ---
            eshmia_entry = db.Eshmia(
                modelo_id=modelo.id,
                valor_eshmia=eshmia_value,
                data_calculo=datetime.datetime.utcnow()
            )
            db_session.add(eshmia_entry)
            print(f"ESHMIA para '{modelo.nome_normalizado}': {eshmia_value:.4f}")
        else:
            print(f"Não foi possível calcular ESHMIA para '{modelo.nome_normalizado}', métricas insuficientes.")

    db_session.commit()
    print("Cálculos concluídos e armazenados.")


if __name__ == '__main__':
    # Bloco para testar o calculador de forma isolada
    print("Testando o calculador de métricas...")
    db_session = next(db.get_db())
    try:
        # Primeiro, executa o coletor para garantir que há dados
        from . import collector
        collector.collect_and_store_data(db_session)
        
        # Agora, executa os cálculos
        calculate_and_store_metrics(db_session)

        # Verifica se os cálculos foram inseridos
        eshmia_count = db_session.query(db.Eshmia).count()
        normalized_count = db_session.query(db.Resultado).filter(db.Resultado.valor_normalizado != None).count()
        
        print(f"Teste concluído: {eshmia_count} entradas ESHMIA e {normalized_count} resultados normalizados no banco.")
        
        # Opcional: Imprimir alguns resultados para verificação
        first_eshmia = db_session.query(db.Eshmia).first()
        if first_eshmia:
            print(f"Exemplo ESHMIA: Modelo ID {first_eshmia.modelo_id}, Valor {first_eshmia.valor_eshmia}")

    finally:
        db_session.close()

