# TCC Data Scraper and Analyzer - Diretrizes de Codificação para IA

## Visão Geral do Projeto
Este é um pipeline ETL em Python para raspagem, processamento e visualização de dados de TCC (Trabalho de Conclusão de Curso) de instituições federais brasileiras. O sistema consiste em três componentes principais:
- **Extração** (`scripts/extracao/`): Interface GUI Tkinter para raspagem assíncrona de web usando aiohttp
- **Transformação** (`scripts/transformacoes/`): Processamento ETL para esquema estrela em SQLite
- **Interface** (`scripts/interface/`): Dashboard Streamlit para visualização de dados

Fluxo de dados: APIs de Instituições → `integra.db` → `datamart.db` → `tccs_dashboard.parquet` → App Streamlit

## Workflows Principais
- **Raspagem**: Execute `python scripts/extracao/main.py` para lançar GUI e raspar instituições selecionadas
- **Processamento**: Execute `python scripts/transformacoes/star_schema.py` para transformar dados brutos
- **Dashboard**: Execute `streamlit run scripts/interface/app.py` para visualizar dados
- **Unificação de Cursos**: Use `python unificar_cursos.py` para correspondência fuzzy de nomes de cursos

## Convenções de Codificação
- **Normalização de Texto**: Sempre use `unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8').lower()` para remover acentos e padronizar (veja `transformacoes/star_schema.py::normalize_string`)
- **Manipulação de Caminhos**: Use `from pathlib import Path; Path(__file__).parent / "file.json"` para caminhos relativos (veja todos os arquivos config.py)
- **Raspagem Assíncrona**: Use aiohttp com limites de semáforo para requests concorrentes (veja `extracao/scraper.py`)
- **Processamento de Dados**: Prefira operações pandas com `.astype(str).str.strip()` para limpeza de texto
- **Correspondência Fuzzy**: Use `rapidfuzz.process.extractOne` para unificação de cursos (veja `unificar_cursos.py`)
- **Cache Streamlit**: Aplique `@st.cache_data` a funções de carregamento de dados (veja `interface/dados.py`)
- **Banco de Dados**: Use SQLAlchemy para operações SQLite, evite SQL puro quando possível
- **Codificação**: Sempre especifique `encoding="utf-8"` para operações de arquivo

## Dependências e Ambiente
- Python 3.8+ com ambiente virtual (`venv/`)
- Instale com `pip install -r requirements.txt` (nota: versão aiohttp pode precisar de atualização para Python 3.13+)
- Bibliotecas principais: pandas, aiohttp, streamlit, sqlalchemy, rapidfuzz, pyarrow

## Padrões de Estrutura de Arquivos
- Arquivos de config carregam JSON da raiz `scripts/` usando navegação Path
- Todos os subdiretórios têm `__init__.py` para estrutura de pacote
- Arquivos Parquet usados para carregamento rápido no dashboard
- Registre registros rejeitados em CSV durante processamento

## Padrões Comuns
- Configs de instituições carregados de `scripts/lista_instituicoes.json`
- Tratamento de erros com try/except e logging no console
- Verificações de validação de dados para colunas obrigatórias antes do processamento
- Filtros na barra lateral no Streamlit usando widgets multiselect

## Pegadinhas
- Garanta variável de ambiente `PYTHONUTF8=1` para codificação adequada
- Arquivos SQLite (`integra.db`, `datamart.db`) são ignorados pelo git
- Limite de correspondência fuzzy tipicamente 85% de similaridade para agrupamento de cursos
- Streamlit requer arquivo parquet no diretório `scripts/interface/`