import pandas as pd
from pathlib import Path

ARQUIVOS = {
    "TCC": Path(r"scripts\interface\tccs_dashboard.parquet"),
    "Artigo": Path(r"scripts\interface\artigos_dashboard.parquet"),
    "Projeto": Path(r"scripts\interface\projetos_dashboard.parquet"),
}

PASTA_SAIDA = Path(r"scripts\testes")
PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

resumos = []

for tipo, caminho in ARQUIVOS.items():
    print("\n" + "=" * 80)
    print(f"TESTANDO: {tipo}")
    print(f"Arquivo: {caminho}")

    if not caminho.exists():
        print("Status: ARQUIVO NÃO ENCONTRADO")
        resumos.append({
            "tipo_arquivo": tipo,
            "arquivo": str(caminho),
            "linhas": None,
            "colunas": None,
            "colunas_nomes": None,
            "contagem_tipo": None,
            "contagem_n_topicos_modelo": None,
            "top_10_topicos": None,
            "arquivo_amostra_csv": None,
            "erro": "Arquivo não encontrado"
        })
        continue

    try:
        df = pd.read_parquet(caminho)

        print("Status: OK")
        print(f"Shape: {df.shape}")
        print(f"Colunas: {df.columns.tolist()}")

        resumo = {
            "tipo_arquivo": tipo,
            "arquivo": str(caminho),
            "linhas": int(df.shape[0]),
            "colunas": int(df.shape[1]),
            "colunas_nomes": ", ".join(df.columns.tolist()),
            "contagem_tipo": None,
            "contagem_n_topicos_modelo": None,
            "top_10_topicos": None,
            "arquivo_amostra_csv": None,
            "erro": None,
        }

        if "tipo" in df.columns:
            contagem_tipo = df["tipo"].value_counts(dropna=False).to_dict()
            resumo["contagem_tipo"] = str(contagem_tipo)
            print("\nContagem por tipo:")
            print(df["tipo"].value_counts(dropna=False))

        if "n_topicos_modelo" in df.columns:
            contagem_topicos = df["n_topicos_modelo"].value_counts(dropna=False).to_dict()
            resumo["contagem_n_topicos_modelo"] = str(contagem_topicos)
            print("\nContagem por número de tópicos do modelo:")
            print(df["n_topicos_modelo"].value_counts(dropna=False))

        if "nome_topico" in df.columns:
            top_10_topicos = df["nome_topico"].value_counts(dropna=False).head(10).to_dict()
            resumo["top_10_topicos"] = str(top_10_topicos)
            print("\nTop 10 tópicos mais frequentes:")
            print(df["nome_topico"].value_counts(dropna=False).head(10))

        amostra = df.head(5).copy()
        amostra["tipo_arquivo"] = tipo

        amostra_saida = PASTA_SAIDA / f"amostra_{tipo.lower()}_dashboard.csv"
        amostra.to_csv(amostra_saida, index=False, encoding="utf-8-sig")
        print(f"\nAmostra salva em: {amostra_saida}")

        resumo["arquivo_amostra_csv"] = str(amostra_saida)
        resumos.append(resumo)

    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        resumos.append({
            "tipo_arquivo": tipo,
            "arquivo": str(caminho),
            "linhas": None,
            "colunas": None,
            "colunas_nomes": None,
            "contagem_tipo": None,
            "contagem_n_topicos_modelo": None,
            "top_10_topicos": None,
            "arquivo_amostra_csv": None,
            "erro": str(e),
        })

df_resumos = pd.DataFrame(resumos)
saida_resumo = PASTA_SAIDA / "resumo_parquets_dashboard.csv"
df_resumos.to_csv(saida_resumo, index=False, encoding="utf-8-sig")

print("\n" + "=" * 80)
print("Teste finalizado.")
print(f"Resumo consolidado salvo em: {saida_resumo}")