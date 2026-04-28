# -*- coding: utf-8 -*-
import streamlit as st
import plotly.express as px
import pandas as pd
from utilitarios import simplificar_topico, metric_bold

def exibir(df_tcc, df_art, df_proj):
    st.subheader("Análise Temática Comparativa")

    # Prepara temas de cada tipo
    def top_temas(df, label, n=10):
        t = df['nome_topico'].value_counts().head(n).reset_index()
        t.columns = ['tema', 'quantidade']
        t['tipo'] = label
        t['tema_simples'] = t['tema'].apply(simplificar_topico)
        return t

    df_t_tcc  = top_temas(df_tcc, 'TCCs')
    df_t_art  = top_temas(df_art, 'Artigos')
    df_t_proj = top_temas(df_proj, 'Projetos')

    # ── MÉTRICAS ──────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_bold("Tema Top TCCs", df_t_tcc.iloc[0]['tema_simples'])
    with col2:
        metric_bold("Tema Top Artigos", df_t_art.iloc[0]['tema_simples'])
    with col3:
        metric_bold("Tema Top Projetos", df_t_proj.iloc[0]['tema_simples'])

    st.markdown("---")

    # ── TOP TEMAS POR TIPO ────────────────────────────────────────────────────
    st.subheader("Top 10 Temas por Tipo")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📚 TCCs**")
        fig1 = px.bar(df_t_tcc, x='quantidade', y='tema_simples', orientation='h',
                      color_discrete_sequence=['#4A90E2'], text='quantidade')
        fig1.update_traces(textposition='outside')
        fig1.update_layout(height=400, showlegend=False,
                           yaxis={'categoryorder': 'total ascending'}, xaxis_title="")
        st.plotly_chart(fig1, config={'responsive': True}, key="dgt_tcc", use_container_width=True)

    with col2:
        st.markdown("**🔬 Artigos**")
        fig2 = px.bar(df_t_art, x='quantidade', y='tema_simples', orientation='h',
                      color_discrete_sequence=['#00CC96'], text='quantidade')
        fig2.update_traces(textposition='outside')
        fig2.update_layout(height=400, showlegend=False,
                           yaxis={'categoryorder': 'total ascending'}, xaxis_title="")
        st.plotly_chart(fig2, config={'responsive': True}, key="dgt_art", use_container_width=True)

    with col3:
        st.markdown("**🗂️ Projetos**")
        fig3 = px.bar(df_t_proj, x='quantidade', y='tema_simples', orientation='h',
                      color_discrete_sequence=['#FFA15A'], text='quantidade')
        fig3.update_traces(textposition='outside')
        fig3.update_layout(height=400, showlegend=False,
                           yaxis={'categoryorder': 'total ascending'}, xaxis_title="")
        st.plotly_chart(fig3, config={'responsive': True}, key="dgt_proj", use_container_width=True)

    st.markdown("---")

    # ── EVOLUÇÃO TEMPORAL POR TEMA ────────────────────────────────────────────
    st.subheader("Evolução Temporal — Top 5 Temas de TCCs")
    top5_tcc = df_t_tcc.head(5)['tema'].tolist()
    df_tempo = df_tcc[df_tcc['nome_topico'].isin(top5_tcc)].groupby(['ano', 'nome_topico']).size().reset_index(name='count')
    df_tempo['tema_simples'] = df_tempo['nome_topico'].apply(simplificar_topico)
    fig_tempo = px.line(df_tempo, x='ano', y='count', color='tema_simples', markers=True,
                        labels={'count': 'TCCs', 'ano': 'Ano', 'tema_simples': 'Tema'})
    fig_tempo.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig_tempo, config={'responsive': True}, key="dgt_tempo", use_container_width=True)

    st.markdown("---")

    # ── MAPA DE CALOR TEMAS × TIPO ────────────────────────────────────────────
    st.subheader("Mapa de Calor: Temas em Comum × Tipo")
    temas_tcc  = set(df_tcc['nome_topico'].dropna().unique())
    temas_art  = set(df_art['nome_topico'].dropna().unique())
    temas_proj = set(df_proj['nome_topico'].dropna().unique())
    todos_temas = list(temas_tcc | temas_art | temas_proj)[:20]

    dados_heat = []
    for tema in todos_temas:
        dados_heat.append({
            'tema': simplificar_topico(tema),
            'TCCs':     len(df_tcc[df_tcc['nome_topico'] == tema]),
            'Artigos':  len(df_art[df_art['nome_topico'] == tema]),
            'Projetos': len(df_proj[df_proj['nome_topico'] == tema]),
        })

    df_heat = pd.DataFrame(dados_heat).set_index('tema')
    fig_heat = px.imshow(df_heat, labels=dict(x="Tipo", y="Tema", color="Quantidade"),
                         aspect='auto', color_continuous_scale='Blues')
    fig_heat.update_layout(height=500)
    st.plotly_chart(fig_heat, config={'responsive': True}, key="dgt_heat", use_container_width=True)