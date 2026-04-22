# -*- coding: utf-8 -*-
import streamlit as st
import plotly.express as px
from utilitarios import simplificar_topico, metric_bold

def exibir(df):
    st.subheader("Visão Geral — Projetos Acadêmicos")

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_bold("Total de Projetos", f"{len(df):,}".replace(",", "."))
    with col2:
        metric_bold("Instituições", df['instituicao'].nunique())
    with col3:
        total_autores = df['autores'].dropna().str.split(',').explode().str.strip().nunique()
        metric_bold("Autores Únicos", f"{total_autores:,}".replace(",", "."))

    st.markdown("---")

    col_left, col_right = st.columns(2)
    with col_left:
# Distribuição por natureza
        st.subheader("Distribuição por Natureza do Projeto")
    df_nat = df['natureza'].value_counts().reset_index()
    df_nat.columns = ['Natureza', 'Projetos']

    col_nat1, col_nat2 = st.columns(2)
    with col_nat1:
        fig_pizza = px.pie(df_nat, values='Projetos', names='Natureza', hole=0.4,
                           color_discrete_sequence=px.colors.qualitative.Bold)
        fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
        fig_pizza.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_pizza, config={'responsive': True}, key="pvg_nat_pizza", use_container_width=True)
    with col_nat2:
        fig_bar = px.bar(df_nat, x='Natureza', y='Projetos',
                         color='Natureza', color_discrete_sequence=px.colors.qualitative.Bold,
                         text='Projetos', labels={'Projetos': 'Quantidade', 'Natureza': ''})
        fig_bar.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig_bar.update_layout(height=400, showlegend=False, xaxis_title="", yaxis_title="Quantidade")
        st.plotly_chart(fig_bar, config={'responsive': True}, key="pvg_nat_bar", use_container_width=True)

    st.markdown("---")

    st.subheader("Natureza dos Projetos por Instituição")
    top10_inst = df['instituicao'].value_counts().head(10).index.tolist()
    df_inst_nat = df[df['instituicao'].isin(top10_inst)].groupby(['instituicao', 'natureza']).size().reset_index(name='count')
    fig_empilhado = px.bar(df_inst_nat, x='instituicao', y='count', color='natureza',
                           color_discrete_sequence=px.colors.qualitative.Bold,
                           labels={'count': 'Projetos', 'instituicao': 'Instituição', 'natureza': 'Natureza'},
                           barmode='stack')
    fig_empilhado.update_layout(height=450, xaxis_tickangle=-30, xaxis_title="", yaxis_title="Quantidade")
    st.plotly_chart(fig_empilhado, config={'responsive': True}, key="pvg_inst_nat", use_container_width=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Produção Anual de Projetos")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 5 Instituições")
        top_inst = df['instituicao'].value_counts().head(5).reset_index()
        top_inst.columns = ['Instituição', 'Projetos']
        st.dataframe(top_inst, hide_index=True, use_container_width=True)
    with col2:
        st.subheader("Top 10 Veículos")
        if df['veiculo'].notna().any():
            top_v = df['veiculo'].dropna().value_counts().head(10).reset_index()
            top_v.columns = ['Veículo', 'Projetos']
            st.dataframe(top_v, hide_index=True, use_container_width=True)
        else:
            st.info("Dados de veículo não disponíveis.")

    st.markdown("---")
    st.subheader("Tabela de Projetos")
    st.markdown(f"**Total exibido:** {len(df):,} registros".replace(",", "."))
    cols = [c for c in ['titulo', 'autores', 'ano', 'instituicao', 'veiculo', 'nome_topico'] if c in df.columns]
    st.dataframe(df[cols].sort_values('ano', ascending=False), hide_index=True, use_container_width=True)