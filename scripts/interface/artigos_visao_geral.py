# -*- coding: utf-8 -*-
import streamlit as st
import plotly.express as px
from utilitarios import simplificar_topico, metric_bold

def exibir(df):
    st.subheader("Visão Geral — Artigos Científicos")

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_bold("Total de Artigos", f"{len(df):,}".replace(",", "."))
    with col2:
        metric_bold("Instituições", df['instituicao'].nunique())
    with col3:
        total_autores = df['autores'].dropna().str.split(',').explode().str.strip().nunique()
        metric_bold("Autores Únicos", f"{total_autores:,}".replace(",", "."))
    # with col4:
    #     metric_bold("Temas", df['nome_topico'].nunique())

    st.markdown("---")

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Produção Anual de Artigos")
        df_ano = df.groupby('ano').size().reset_index(name='count')
        fig = px.bar(df_ano, x='ano', y='count', labels={'count': 'Quantidade', 'ano': 'Ano'})
        fig.update_layout(height=400, showlegend=False, yaxis_title="Quantidade de Artigos")
        st.plotly_chart(fig, config={'responsive': True}, key="avg_1")

    with col_right:
        st.subheader("Distribuição por Tema")
        df_top = df['nome_topico'].value_counts().head(8).reset_index()
        df_top.columns = ['tema', 'count']
        df_top['tema_simples'] = df_top['tema'].apply(simplificar_topico)
        fig2 = px.pie(df_top, values='count', names='tema_simples', hole=0.4)
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, config={'responsive': True}, key="avg_2")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 5 Instituições")
        top_inst = df['instituicao'].value_counts().head(5).reset_index()
        top_inst.columns = ['Instituição', 'Artigos']
        st.dataframe(top_inst, hide_index=True, use_container_width=True)
    with col2:
        st.subheader("Top 10 Veículos de Publicação")
        if df['veiculo'].notna().any():
            top_v = df['veiculo'].dropna().value_counts().head(10).reset_index()
            top_v.columns = ['Veículo', 'Artigos']
            st.dataframe(top_v, hide_index=True, use_container_width=True)
        else:
            st.info("Dados de veículo não disponíveis.")

    st.markdown("---")
    st.subheader("Tabela de Artigos")
    st.markdown(f"**Total exibido:** {len(df):,} registros".replace(",", "."))
    cols = [c for c in ['titulo', 'autores', 'ano', 'instituicao', 'veiculo', 'nome_topico'] if c in df.columns]
    st.dataframe(df[cols].sort_values('ano', ascending=False), hide_index=True, use_container_width=True)