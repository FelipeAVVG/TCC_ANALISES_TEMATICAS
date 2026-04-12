# TCC_ANALISSES_TEMATICAS

scripts/
│
├── extracao/
│   ├── __init__.py
│   ├── config.py              # Carregamento de configurações e instituições
│   ├── crawler.py             # Funções de requests e scraping
│   ├── processamento.py       # Funções de processamento/transformação dos dados
│   └── main.py                # Orquestrador (executa tudo)
│
└── banco/
    ├── __init__.py
    └── database.py            # Conexão e operações no SQLite

## Novidades

- O scraper agora coleta também **artigos científicos e Projetos academicos** associados a cada professor, além dos TCCs. Os registros são salvos em uma tabela `artigos` e a tabela `projetos` no banco de dados.
- O pipeline de transformação (`star_schema.py` e `preprocess.py`) trata esse novo conjunto de dados e o dashboard do Streamlit inclui filtro por tipo de registro (TCC/Artigo).

