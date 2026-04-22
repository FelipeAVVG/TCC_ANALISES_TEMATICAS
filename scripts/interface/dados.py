

# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os

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
        df = pd.read_parquet(file_path)

        required_cols = COLUNAS_OBRIGATORIAS.get(nome_arquivo, [])
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Colunas faltando em '{nome_arquivo}': {missing}")
            st.stop()

        # Normalizar ano apenas se tiver dados válidos
        if 'ano' in df.columns:
            df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
            df_com_ano = df.dropna(subset=['ano'])
            if not df_com_ano.empty:
                df = df_com_ano
                df['ano'] = df['ano'].astype(int)

        if df.empty:
            st.error(f"Nenhum registro válido encontrado em '{nome_arquivo}'.")
            st.stop()

        return df

    except FileNotFoundError:
        st.error(f"Arquivo '{nome_arquivo}' não encontrado.")
        st.stop()

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.stop()