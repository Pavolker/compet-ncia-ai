
from backend.database import get_db, Modelo, Eshmia
import pandas as pd

def show_table():
    db = next(get_db())
    try:
        modelos = db.query(Modelo).all()
        data = []
        for m in modelos:
            eshmia_val = None
            if m.eshmias:
                eshmia_val = m.eshmias[0].valor_eshmia
            
            row = {
                "Model": m.nome_normalizado,
                "ESHMIA": eshmia_val
            }
            # Add specific metrics if needed, but simplistic view for now
            for res in m.resultados:
                row[res.metrica.nome] = res.valor_cru
            
            data.append(row)
        
        if not data:
            print("Nenhum modelo válido encontrado no banco de dados para o cálculo do ESHMIA.")
            print("Verifique se o arquivo dados.csv contém valores válidos para: IFEval, BBH, MATH, GPQA, MUSR, MMLU-PRO.")
            return

        df = pd.DataFrame(data)
        cols = ["Model", "IFEval", "BBH", "MATH", "GPQA", "MUSR", "MMLU-PRO", "ESHMIA"]
        # Ensure columns exist
        for c in cols:
            if c not in df.columns:
                df[c] = None
        
        print(df[cols].to_string(index=False))

        # Stats
        if "ESHMIA" in df.columns and not df["ESHMIA"].isnull().all():
            best = df.loc[df["ESHMIA"].idxmax()]
            worst = df.loc[df["ESHMIA"].idxmin()]
            avg = df["ESHMIA"].mean()
            print("\n----- Estatísticas -----")
            print(f"Melhor Modelo: {best['Model']} ({best['ESHMIA']:.4f})")
            print(f"Pior Modelo: {worst['Model']} ({worst['ESHMIA']:.4f})")
            print(f"Média Geral ESHMIA: {avg:.4f}")

    finally:
        db.close()

if __name__ == "__main__":
    show_table()
