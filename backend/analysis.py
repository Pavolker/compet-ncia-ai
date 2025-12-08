def generate_analysis(data: dict) -> str:
    """
    Gera uma análise qualitativa detalhada sobre o progresso dos modelos de IA
    em direção à paridade humana, baseada no Índice ESHMIA.
    """
    eshmia_medio = data.get("eshmia_medio", 0)
    modelos = data.get("modelos", [])
    metricas = data.get("metricas_agregadas", {})
    
    if not modelos or not metricas:
        return "Dados insuficientes para gerar a análise qualitativa do ecossistema."

    # Mapeamento semântico das competências
    competencias = {
        "IFEval": "Obediência (seguir instruções)",
        "BBH": "Raciocínio (lógica)",
        "MATH": "Cálculo (matemática)",
        "GPQA": "Ciência (nível acadêmico)",
        "MUSR": "Diálogo (interação complexa)",
        "MMLU-PRO": "Conhecimento (profissional)"
    }

    # Encontrar métricas de maior e menor performance média
    metricas_ordenadas = []
    for codigo, dados in metricas.items():
        media = dados.get('media', 0)
        nome_competencia = competencias.get(codigo, codigo)
        metricas_ordenadas.append((media, nome_competencia))
    
    # Ordena: maior para menor
    metricas_ordenadas.sort(key=lambda x: x[0], reverse=True)
    
    melhor_competencia = metricas_ordenadas[0]
    pior_competencia = metricas_ordenadas[-1]
    
    # Modelo líder
    modelo_lider = max(modelos, key=lambda m: m.get("valor_eshmia", 0))
    nome_lider = modelo_lider['nome_normalizado'].replace('-', ' ').title()
    eshmia_lider = modelo_lider.get('valor_eshmia', 0)

    # Construção do texto narrativo
    texto = (
        f"Monitoramento do Ecossistema de IA:\n\n"
        f"Atualmente, os modelos de Inteligência Artificial monitorados apresentam uma eficiência média de {(eshmia_medio * 100):.1f}% "
        f"em relação à performance humana de referência (1.0).\n\n"
        
        f"Na análise qualitativa das competências, o ecossistema mostra maior maturidade em "
        f"**{melhor_competencia[1]}**, atingindo {(melhor_competencia[0] * 100):.1f}% do nível humano. "
        f"Isso indica que as IAs já estão altamente capazes de {melhor_competencia[1].split('(')[1].replace(')', '')}.\n\n"
        
        f"Por outro lado, o maior desafio atual reside na competência de **{pior_competencia[1]}**, "
        f"onde a média do ecossistema é de {(pior_competencia[0] * 100):.1f}%. "
        f"Ainda existe uma lacuna significativa para atingir a paridade humana em habilidades de {pior_competencia[1].split('(')[1].replace(')', '')}.\n\n"
        
        f"O modelo de referência atual é o **{nome_lider}**, com um ESHMIA individual de {eshmia_lider:.4f}, "
        f"representando o estado da arte na aproximação das capacidades cognitivas humanas."
    )
    
    return texto