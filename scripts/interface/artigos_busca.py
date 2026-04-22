# -*- coding: utf-8 -*-
import streamlit as st
from utilitarios import calcular_similaridade

def exibir(df):
    st.subheader("Busca de Artigos Científicos")

    col1, col2 = st.columns([3, 1])
    with col1:
        termo = st.text_input("🔍 Buscar por título, autor ou resumo", placeholder="Ex: inteligência artificial, redes neurais...")
    with col2:
        campo = st.selectbox("Campo", ["Título", "Autor", "Resumo"])

    if termo:
        termo_lower = termo.lower()
        if campo == "Título":
            resultado = df[df['titulo'].str.lower().str.contains(termo_lower, na=False)]
        elif campo == "Autor":
            resultado = df[df['autores'].str.lower().str.contains(termo_lower, na=False)]
        else:
            resultado = df[df['resumo'].str.lower().str.contains(termo_lower, na=False)]

        st.markdown(f"**{len(resultado)} artigo(s) encontrado(s)**")

        if not resultado.empty:
            cols = [c for c in ['titulo', 'autores', 'ano', 'instituicao', 'veiculo', 'nome_topico'] if c in df.columns]
            st.dataframe(resultado[cols].sort_values('ano', ascending=False), hide_index=True, use_container_width=True)

            # Similaridade
            st.markdown("---")
            st.subheader("Artigos Similares ao Primeiro Resultado")
            idx = df.index.get_loc(resultado.index[0])
            df_reset = df.reset_index(drop=True)
            similares = calcular_similaridade(df_reset, idx, top_n=5)
            if not similares.empty:
                cols_sim = [c for c in ['titulo', 'autores', 'ano', 'instituicao', 'similaridade'] if c in similares.columns]
                st.dataframe(similares[cols_sim], hide_index=True, use_container_width=True)
        else:
            st.info("Nenhum artigo encontrado. Tente outro termo.")
    else:
        st.info("Digite um termo acima para buscar artigos.")
        st.markdown("---")
        st.subheader("Artigos Recentes")
        cols = [c for c in ['titulo', 'autores', 'ano', 'instituicao', 'veiculo', 'nome_topico'] if c in df.columns]
        st.dataframe(df[cols].sort_values('ano', ascending=False).head(20), hide_index=True, use_container_width=True)