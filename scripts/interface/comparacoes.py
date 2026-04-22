# -*- coding: utf-8 -*-
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utilitarios import metric_bold


def exibir(df_tcc, df_art, df_proj):
    # st.subheader("Comparações entre TCCs, Artigos e Projetos")

        # ── MÉTRICAS GERAIS ───────────────────────────────────────────────────────
    st.subheader("Visão Geral da Produção")
    col1, col2, col3, col4 = st.columns(4)
    total = len(df_tcc) + len(df_art) + len(df_proj)
    with col1:
        metric_bold("Total Geral", f"{total:,}".replace(",", "."))
    with col2:
        metric_bold("TCCs", f"{len(df_tcc):,}".replace(",", "."))
    with col3:
        metric_bold("Artigos", f"{len(df_art):,}".replace(",", "."))
    with col4:
        metric_bold("Projetos", f"{len(df_proj):,}".replace(",", "."))

    st.markdown("---")

    # ── FILTRO DE INSTITUIÇÃO ─────────────────────────────────────────────────
    todas_inst = sorted(set(
        df_tcc['instituicao'].dropna().unique().tolist() +
        df_art['instituicao'].dropna().unique().tolist() +
        df_proj['instituicao'].dropna().unique().tolist()
    ))
    inst_sel = st.multiselect("Filtrar por Instituição (deixe vazio para todas)", options=todas_inst)

    if inst_sel:
        df_tcc  = df_tcc[df_tcc['instituicao'].isin(inst_sel)]
        df_art  = df_art[df_art['instituicao'].isin(inst_sel)]
        df_proj = df_proj[df_proj['instituicao'].isin(inst_sel)]
        

    # ── PIZZA GERAL ───────────────────────────────────────────────────────────
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Distribuição Geral")
        df_dist = pd.DataFrame({
            'Tipo': ['TCCs', 'Artigos', 'Projetos'],
            'Quantidade': [len(df_tcc), len(df_art), len(df_proj)]
        })
        fig_pizza = px.pie(df_dist, values='Quantidade', names='Tipo', hole=0.4,
                           color_discrete_sequence=['#4A90E2', '#00CC96', '#FFA15A'])
        fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
        fig_pizza.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_pizza, config={'responsive': True}, key="cmp_pizza", use_container_width=True)

    with col_right:
        st.subheader("Produção por Tipo")
        fig_bar = px.bar(df_dist, x='Tipo', y='Quantidade', color='Tipo',
                         color_discrete_sequence=['#4A90E2', '#00CC96', '#FFA15A'],
                         text='Quantidade')
        fig_bar.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig_bar.update_layout(height=350, showlegend=False, xaxis_title="", yaxis_title="Quantidade")
        st.plotly_chart(fig_bar, config={'responsive': True}, key="cmp_bar_geral", use_container_width=True)

    st.markdown("---")

    # ── EVOLUÇÃO TEMPORAL ─────────────────────────────────────────────────────
    st.subheader("Evolução Temporal da Produção")
    df_tcc_ano  = df_tcc.groupby('ano').size().reset_index(name='count')
    df_tcc_ano['tipo'] = 'TCCs'
    df_art_ano  = df_art.groupby('ano').size().reset_index(name='count')
    df_art_ano['tipo'] = 'Artigos'
    df_tempo = pd.concat([df_tcc_ano, df_art_ano])
    df_tempo = df_tempo[df_tempo['ano'] >= 1960]
    fig_tempo = px.line(df_tempo, x='ano', y='count', color='tipo', markers=True)
    fig_tempo.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig_tempo, config={'responsive': True}, key="cmp_tempo", use_container_width=True)
    st.caption("⚠️ Projetos não possuem dados de ano disponíveis.")

    st.markdown("---")

# ── RANKING DE IFs POR TIPO ───────────────────────────────────────────────
    st.subheader("Ranking de Instituições por Tipo de Produção")

    top_tcc = df_tcc['instituicao'].value_counts().head(10).reset_index()
    top_tcc.columns = ['Instituição', 'Quantidade']
    top_tcc['Tipo'] = 'TCCs'

    top_art = df_art['instituicao'].value_counts().head(10).reset_index()
    top_art.columns = ['Instituição', 'Quantidade']
    top_art['Tipo'] = 'Artigos'

    top_proj = df_proj['instituicao'].value_counts().head(10).reset_index()
    top_proj.columns = ['Instituição', 'Quantidade']
    top_proj['Tipo'] = 'Projetos'

    for label, df_rank, key, cor in [
        ("📚 Top 10 — TCCs",     top_tcc,  "cmp_rank_tcc",  '#4A90E2'),
        ("🔬 Top 10 — Artigos",  top_art,  "cmp_rank_art",  '#00CC96'),
        ("🗂️ Top 10 — Projetos", top_proj, "cmp_rank_proj", '#FFA15A'),
    ]:
        st.markdown(f"**{label}**")
        fig = px.bar(df_rank, x='Quantidade', y='Instituição', orientation='h',
                     color_discrete_sequence=[cor], text='Quantidade')
        fig.update_traces(textposition='outside')
        fig.update_layout(height=400, showlegend=False,
                          yaxis={'categoryorder': 'total ascending'},
                          margin=dict(l=200, r=50),
                          xaxis_title="Quantidade")
        st.plotly_chart(fig, config={'responsive': True}, key=key, use_container_width=True)

    st.markdown("---")

    # ── COMPARAÇÃO POR IF ─────────────────────────────────────────────────────
    st.subheader("Comparação por Instituição")
    st.caption("Top 10 IFs com maior produção de TCCs comparadas nos 3 tipos")

    top_inst_geral = df_tcc['instituicao'].value_counts().head(10).index.tolist()
    df_comp = pd.DataFrame({
        'Instituição': top_inst_geral,
        'TCCs':     [len(df_tcc[df_tcc['instituicao'] == i]) for i in top_inst_geral],
        'Artigos':  [len(df_art[df_art['instituicao'] == i]) for i in top_inst_geral],
        'Projetos': [len(df_proj[df_proj['instituicao'] == i]) for i in top_inst_geral],
    })
    df_comp_melted = df_comp.melt(id_vars='Instituição', var_name='Tipo', value_name='Quantidade')
    fig_comp = px.bar(df_comp_melted, x='Instituição', y='Quantidade', color='Tipo',
                      barmode='group',
                      color_discrete_map={'TCCs': '#4A90E2', 'Artigos': '#00CC96', 'Projetos': '#FFA15A'},
                      labels={'Quantidade': 'Quantidade', 'Instituição': ''},
                      text='Quantidade')
    fig_comp.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig_comp.update_layout(height=500, xaxis_tickangle=-30,
                           xaxis_title="", yaxis_title="Quantidade",
                           legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig_comp, config={'responsive': True}, key="cmp_por_if", use_container_width=True)