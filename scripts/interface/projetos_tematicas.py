# -*- coding: utf-8 -*-
import streamlit as st
import plotly.express as px
from utilitarios import simplificar_topico, extract_keywords, metric_bold

def exibir(df):
    st.subheader("Análise Temática — Projetos Acadêmicos")

    df_temas = df.groupby('nome_topico').agg(
        qtd=('titulo', 'count'),
        qtd_instituicoes=('instituicao', 'nunique')
    ).reset_index()
    df_temas.columns = ['tema', 'qtd', 'qtd_instituicoes']
    df_temas = df_temas.sort_values('qtd', ascending=False)
    df_temas['tema_simples'] = df_temas['tema'].apply(simplificar_topico)

    col1, col2 = st.columns(2)
    with col1:
        tema_top = df_temas.iloc[0]['tema_simples'] if not df_temas.empty else 'N/A'
        metric_bold("Tema Mais Frequente", tema_top)
    with col2:
        metric_bold("Média Projetos/Tema", f"{df_temas['qtd'].mean():.1f}")

    st.markdown("---")

    st.subheader("Análise por Tema")
    tema_sel = st.selectbox("Selecione um tema", options=df_temas['tema'].tolist(), format_func=simplificar_topico)
    if tema_sel:
        df_det = df[df['nome_topico'] == tema_sel]
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Projetos", len(df_det))
        with col_b:
            st.metric("Instituições", df_det['instituicao'].nunique())
        with col_c:
            if df_det['natureza'].notna().any():
                nat_top = df_det['natureza'].value_counts().index[0]
                st.metric("Natureza Principal", nat_top)

        st.write("**Top Palavras-Chave:**")
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
        st.subheader("Distribuição por Natureza neste Tema")
        if df_det['natureza'].notna().any():
            df_nat = df_det['natureza'].value_counts().reset_index()
            df_nat.columns = ['Natureza', 'Projetos']
            fig_nat = px.bar(df_nat, x='Natureza', y='Projetos',
                             color='Natureza', color_discrete_sequence=px.colors.qualitative.Bold,
                             text='Projetos')
            fig_nat.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig_nat.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig_nat, config={'responsive': True}, key="ptm_nat")

    st.markdown("---")
    st.subheader("Mapa de Calor: Temas × Instituições")
    top_inst_heatmap = df['instituicao'].value_counts().head(6).index.tolist()
    top_temas_heatmap = df_temas.head(6)['tema'].tolist()
    df_heatmap = df[(df['instituicao'].isin(top_inst_heatmap)) & (df['nome_topico'].isin(top_temas_heatmap))]
    if not df_heatmap.empty:
        pivot_table = df_heatmap.pivot_table(index='nome_topico', columns='instituicao', values='titulo', aggfunc='count', fill_value=0)
        pivot_table.index = pivot_table.index.map(simplificar_topico)
        fig3 = px.imshow(pivot_table, labels=dict(x="Instituição", y="Tema", color="Projetos"), aspect='auto')
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, config={'responsive': True}, key="ptm_3")
    else:
        st.info("Dados insuficientes para gerar o mapa de calor.")