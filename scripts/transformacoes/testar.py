import pandas as pd

# Lê o parquet
df = pd.read_parquet(r"scripts\interface\producoes_dashboard.parquet")

# Mostra informações básicas
print(df.shape)
print(df.columns.tolist())
print(df["tipo"].value_counts(dropna=False))

# Pega uma pequena amostra de cada tipo
amostra_tcc = df[df["tipo"] == "TCC"].head(100)
amostra_artigo = df[df["tipo"] == "Artigo"].head(100)
amostra_projeto = df[df["tipo"] == "Projeto"].head(100)

# Junta tudo em um único DataFrame
amostra_final = pd.concat([amostra_tcc, amostra_artigo, amostra_projeto], ignore_index=True)

# Mostra a amostra no terminal
print(amostra_final)

# Salva em CSV
amostra_final.to_csv(
    r"scripts\interface\amostra_producoes_dashboard.csv",
    index=False,
    encoding="utf-8-sig"
)

print("CSV gerado com sucesso: scripts\\interface\\amostra_producoes_dashboard.csv")