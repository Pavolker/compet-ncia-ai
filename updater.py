import os
import json
import pandas as pd
from google import genai
from google.genai import types
from datetime import datetime

# Configurações
API_KEY = "AIzaSyAVmjvUrIWeTy_-NVcHI6TiESYjhBj5JMc"
CSV_FILE = "big_benchmarks_top100.csv"

def fetch_live_data():
    """Usa a nova SDK google-genai para buscar os dados mais recentes."""
    print("🚀 Iniciando coleta via Google GenAI SDK (Live Search)...")
    
    client = genai.Client(api_key=API_KEY)
    
    prompt = """
    Acesse a "Hugging Face Open LLM Leaderboard v2" (The Big Benchmarks Collection).
    BUSQUE pelos modelos que estão no topo HOJE (Janeiro de 2026), como Llama 3.1, Claude 3.5, GPT-4o, Gemini 1.5 Pro, Nemotron, etc.
    
    Extraia os dados dos TOP 50 modelos mais bem ranqueados.
    
    Para cada modelo, extraia as seguintes métricas exatas:
    - rank
    - type
    - model (nome exato no leaderboard)
    - average (entre 0 e 100)
    - ifeval (0-100)
    - bbh (0-100)
    - math (0-100)
    - gpqa (0-100)
    - musr (0-100)
    - mmlu_pro (0-100)
    - co2_cost
    
    Retorne o resultado APENAS como um Array JSON de objetos.
    Não adicione explicações ou markdown.
    """

    print("📡 Consultando Gemini 2.0 Flash com Live Search...")
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        data = json.loads(text)
        if isinstance(data, list):
            print(f"✅ Recebidos {len(data)} registros da IA.")
            for i, m in enumerate(data[:5]):
                print(f"   Model Ranking {i+1}: {m.get('model')} (Score: {m.get('average')})")
        return data
    except Exception as e:
        print(f"❌ Erro ao processar resposta da IA: {e}")
        return None

def update_csv(data):
    """Atualiza o arquivo CSV local com os novos dados."""
    if not data or not isinstance(data, list):
        print("⚠️ Dados inválidos ou vazios.")
        return False
        
    print(f"💾 Atualizando {CSV_FILE}...")
    df = pd.DataFrame(data)
    
    # Normaliza nomes de colunas (caso a IA retorne variações)
    df.columns = [c.lower().replace('-', '_') for c in df.columns]
    
    # Colunas esperadas
    cols = ['rank', 'type', 'model', 'average', 'ifeval', 'bbh', 'math', 'gpqa', 'musr', 'mmlu_pro', 'co2_cost']
    
    # Garante que todas as colunas existam
    for col in cols:
        if col not in df.columns:
            df[col] = 0.0
            
    df = df[cols]
    df.to_csv(CSV_FILE, index=False)
    print("✅ CSV atualizado com sucesso!")
    return True

if __name__ == "__main__":
    live_data = fetch_live_data()
    if update_csv(live_data):
        print(f"\n✨ Dados atualizados para hoje: {datetime.now().strftime('%d/%m/%Y')}")
    else:
        print("\n⚠️ Falha na atualização.")
