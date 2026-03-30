import pandas as pd

df = pd.read_parquet(r"scripts\interface\tccs_dashboard.parquet")
print(df.shape)
print(df.columns.tolist())
print(df["tipo"].value_counts(dropna=False))
print(df.head(50))