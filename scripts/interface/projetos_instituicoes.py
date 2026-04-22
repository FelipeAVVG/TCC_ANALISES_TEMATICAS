# -*- coding: utf-8 -*-
import streamlit as st
import plotly.express as px
from utilitarios import metric_bold

def exibir(df):
    st.subheader("Análise por Instituição — Projetos Acadêmicos")

    col1, col2 = st.columns(2)
    with col1:
        metric_bold("Total de Instituições", df['instituicao'].nunique())
    with col2:
        top_inst_nome = df['instituicao'].value_counts().index[0]
        metric_bold("Instituição Mais Ativa", top_inst_nome)

    st.markdown("---")

    st.subheader("Ranking de Instituições por Produção")
    top_inst = df['instituicao'].value_counts().reset_index()
    top_inst.columns = ['Instituição', 'Projetos']
    fig = px.bar(top_inst.head(15), x='Projetos', y='Instituição', orientation='h',
                 labels={'Projetos': 'Quantidade', 'Instituição': ''},
                 color='Projetos', color_continuous_scale='Blues')
    fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'}, showlegend=False)
    st.plotly_chart(fig, config={'responsive': True}, key="pin_1")

    st.markdown("---")

    st.subheader("Produção Anual por Instituição")
    top5 = df['instituicao'].value_counts().head(5).index.tolist()
    df_tempo = df[df['instituicao'].isin(top5)].groupby(['ano', 'instituicao']).size().reset_index(name='count')
    fig2 = px.line(df_tempo, x='ano', y='count', color='instituicao', markers=True,
                   labels={'count': 'Projetos', 'ano': 'Ano', 'instituicao': 'Instituição'})
    fig2.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig2, config={'responsive': True}, key="pin_2")

    st.markdown("---")

    st.subheader("Detalhamento por Instituição")
    inst_sel = st.selectbox("Selecione uma instituição", options=sorted(df['instituicao'].dropna().unique()))
    if inst_sel:
        df_inst = df[df['instituicao'] == inst_sel]
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total de Projetos", len(df_inst))
        with col_b:
            st.metric("Temas", df_inst['nome_topico'].nunique())
        with col_c:
            autores = df_inst['autores'].dropna().str.split(',').explode().str.strip().nunique()
            st.metric("Autores Únicos", autores)

        cols = [c for c in ['titulo', 'autores', 'ano', 'veiculo', 'nome_topico'] if c in df.columns]
        st.dataframe(df_inst[cols].sort_values('ano', ascending=False), hide_index=True, use_container_width=True)
