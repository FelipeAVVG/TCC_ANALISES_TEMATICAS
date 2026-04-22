# -*- coding: utf-8 -*-
import streamlit as st
import plotly.express as px
from utilitarios import simplificar_topico, extract_keywords, metric_bold

def exibir(df):
    st.subheader("Análise Temática — Projetos Acadêmicos")

    df_temas = df.groupby('nome_topico').agg(
        qtd=('titulo', 'count'),
        instituicoes=('instituicao', 'nunique')
    ).reset_index().sort_values('qtd', ascending=False)
    df_temas['tema_simples'] = df_temas['nome_topico'].apply(simplificar_topico)

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_bold("Total de Temas", len(df_temas))
    with col2:
        tema_top = df_temas.iloc[0]['tema_simples'] if not df_temas.empty else 'N/A'
        metric_bold("Tema Mais Frequente", tema_top)
    with col3:
        metric_bold("Média Projetos/Tema", f"{df_temas['qtd'].mean():.1f}")

    st.markdown("---")

    if 'ano' in df.columns and df['ano'].notna().any():
        st.subheader("Evolução Temporal dos Principais Temas")
        top_temas = df_temas.head(5)['nome_topico'].tolist()
        df_tempo = df[df['nome_topico'].isin(top_temas)].groupby(['ano', 'nome_topico']).size().reset_index(name='count')
        df_tempo['tema_simples'] = df_tempo['nome_topico'].apply(simplificar_topico)
        fig = px.line(df_tempo, x='ano', y='count', color='tema_simples', markers=True,
                      labels={'count': 'Projetos', 'ano': 'Ano', 'tema_simples': 'Tema'})
        fig.update_layout(height=400, hovermode='x unified')
        st.plotly_chart(fig, config={'responsive': True}, key="ptm_1")
    else:
        st.info("⚠️ Dados de ano não disponíveis para projetos.")

    st.markdown("---")

    st.subheader("Análise por Tema")
    tema_sel = st.selectbox("Selecione um tema", options=df_temas['nome_topico'].tolist(), format_func=simplificar_topico)
    if tema_sel:
        df_det = df[df['nome_topico'] == tema_sel]

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Projetos", len(df_det))
        with col_b:
            st.metric("Instituições", df_det['instituicao'].nunique())

        st.write("**Top Palavras-Chave dos Resumos:**")
        keywords = extract_keywords(df_det['resumo_processado'], top_n=10)
        col1, col2 = st.columns(2)
        metade = len(keywords) // 2
        with col1:
            for word, freq in keywords[:metade]:
                st.write(f"• {word}: {freq} ocorrências")
        with col2:
            for word, freq in keywords[metade:]:
                st.write(f"• {word}: {freq} ocorrências")

        st.markdown("---")
        st.subheader("Top Veículos neste Tema")
        if df_det['veiculo'].notna().any():
            top_v = df_det['veiculo'].dropna().value_counts().head(8).reset_index()
            top_v.columns = ['Veículo', 'Projetos']
            fig2 = px.bar(top_v, x='Projetos', y='Veículo', orientation='h',
                          labels={'Projetos': 'Quantidade', 'Veículo': ''})
            fig2.update_layout(height=350, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig2, config={'responsive': True}, key="ptm_2")
        else:
            st.info("Dados de veículo não disponíveis para este tema.")