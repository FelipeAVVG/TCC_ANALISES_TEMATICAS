

# # -*- coding: utf-8 -*-
# import streamlit as st
# import pandas as pd
# import os

# COLUNAS_OBRIGATORIAS = {
#     "tccs_dashboard.parquet":     ['titulo', 'autores', 'ano', 'instituicao', 'resumo', 'resumo_processado', 'curso', 'nome_topico', 'orientador', 'curso_unificado', 'tipo'],
#     "artigos_dashboard.parquet":  ['titulo', 'autores', 'ano', 'instituicao', 'resumo', 'resumo_processado', 'nome_topico', 'orientador', 'tipo'],
#     "projetos_dashboard.parquet": ['titulo', 'autores', 'instituicao', 'resumo', 'resumo_processado', 'nome_topico', 'tipo'],
# }

# @st.cache_data
# def carregar_dados(nome_arquivo="tccs_dashboard.parquet"):
#     try:
#         BASE_DIR = os.path.dirname(__file__)
#         file_path = os.path.join(BASE_DIR, nome_arquivo)
#         df = pd.read_parquet(file_path)

#         required_cols = COLUNAS_OBRIGATORIAS.get(nome_arquivo, [])
#         missing = [c for c in required_cols if c not in df.columns]
#         if missing:
#             st.error(f"Colunas faltando em '{nome_arquivo}': {missing}")
#             st.stop()

#         # Normalizar ano apenas se tiver dados válidos
#         if 'ano' in df.columns:
#             df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
#             df_com_ano = df.dropna(subset=['ano'])
#             if not df_com_ano.empty:
#                 df = df_com_ano
#                 df['ano'] = df['ano'].astype(int)

#         if df.empty:
#             st.error(f"Nenhum registro válido encontrado em '{nome_arquivo}'.")
#             st.stop()

#         return df

#     except FileNotFoundError:
#         st.error(f"Arquivo '{nome_arquivo}' não encontrado.")
#         st.stop()

#     except Exception as e:
#         st.error(f"Erro ao carregar dados: {e}")
#         st.stop()

# -----------

# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
import gdown

DRIVE_IDS = {
    "artigos_dashboard.parquet":  "1PFgyctCUeMIeIaWQhk5VJa1_yVSnuC1z",
    "projetos_dashboard.parquet": "1Inic8ZfwcOV5QE-DfwezmBp5lxgX1xao",
    "tccs_dashboard.parquet":     "18esmAZm20GFo-PNLzXurUJ4ycwO4sGAE",
}

COLUNAS_OBRIGATORIAS = {
    "tccs_dashboard.parquet":     ['titulo', 'autores', 'ano', 'instituicao', 'resumo', 'resumo_processado', 'curso', 'nome_topico', 'orientador', 'curso_unificado', 'tipo'],
    "artigos_dashboard.parquet":  ['titulo', 'autores', 'ano', 'instituicao', 'resumo', 'resumo_processado', 'nome_topico', 'orientador', 'tipo'],
    "projetos_dashboard.parquet": ['titulo', 'autores', 'instituicao', 'resumo', 'resumo_processado', 'nome_topico', 'tipo'],
}

@st.cache_data
def carregar_dados(nome_arquivo="tccs_dashboard.parquet"):
    try:
        BASE_DIR = os.path.dirname(__file__)
        file_path = os.path.join(BASE_DIR, nome_arquivo)

        if not os.path.exists(file_path):
            file_id = DRIVE_IDS.get(nome_arquivo)
            if not file_id:
                st.error(f"ID não configurado para '{nome_arquivo}'.")
                st.stop()
            with st.spinner(f"⬇️ Baixando {nome_arquivo}..."):
                gdown.download(
                    id=file_id,
                    output=file_path,
                    quiet=False,
                    fuzzy=True,
                    resume=True
                )

        if not os.path.exists(file_path) or os.path.getsize(file_path) < 1000:
            st.error(f"Falha ao baixar '{nome_arquivo}'. Tente recarregar a página.")
            st.stop()

        df = pd.read_parquet(file_path)

        required_cols = COLUNAS_OBRIGATORIAS.get(nome_arquivo, [])
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Colunas faltando em '{nome_arquivo}': {missing}")
            st.stop()

        if 'ano' in df.columns:
            df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
            df_com_ano = df.dropna(subset=['ano'])
            if not df_com_ano.empty:
                df = df_com_ano
                df['ano'] = df['ano'].astype(int)

        if df.empty:
            st.error(f"Nenhum registro válido em '{nome_arquivo}'.")
            st.stop()

        return df

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.stop()