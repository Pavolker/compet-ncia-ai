def generate_analysis(data: dict) -> str:
    """
    Gera uma análise textual simples com base nos dados fornecidos.
    Esta é a implementação inicial (Item 8).
    """
    eshmia_medio = data.get("eshmia_medio", 0)
    modelos = data.get("modelos", [])
    
    if not modelos:
        return "Nenhum dado disponível para análise."
        
    # Encontra o modelo com maior ESHMIA
    modelo_lider = max(modelos, key=lambda m: m.get("valor_eshmia", 0))
    nome_lider = modelo_lider['nome_normalizado'].replace('-', ' ').title()
    eshmia_lider = modelo_lider.get('valor_eshmia', 0)

    # Constrói o texto
    texto = (
        f"Análise do Ecossistema de IA:\n\n"
        f"O ESHMIA médio atual do ecossistema é de {eshmia_medio:.4f}. "
        f"Este índice representa a performance média dos modelos em relação ao baseline humano nas métricas IFEval, BBH, MATH, GPQA, MUSR e MMLU-PRO.\n\n"
        f"O modelo em destaque é o {nome_lider}, que alcançou o maior ESHMIA individual de {eshmia_lider:.4f}. "
        f"Isso indica uma performance robusta e equilibrada em todas as métricas avaliadas."
    )
    
    return texto