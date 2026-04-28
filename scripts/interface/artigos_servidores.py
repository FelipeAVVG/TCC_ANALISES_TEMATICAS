# -*- coding: utf-8 -*-
import streamlit as st
import plotly.express as px
from utilitarios import simplificar_topico, metric_bold

def exibir(df):
    st.subheader("Análise de Servidores — Artigos Científicos")

    df_serv = df.groupby('autores').agg(
        qtd=('titulo', 'count'),
        tema_principal=('nome_topico', lambda x: x.mode()[0] if not x.mode().empty else 'N/A'),
        instituicao=('instituicao', lambda x: x.mode()[0] if not x.mode().empty else 'N/A')
    ).reset_index()
    df_serv.columns = ['servidor', 'qtd', 'tema_principal', 'instituicao']
    df_serv = df_serv.sort_values('qtd', ascending=False)

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_bold("Total de Servidores", len(df_serv))
    with col2:
        metric_bold("Média Artigos/Servidor", f"{df_serv['qtd'].mean():.1f}")
    with col3:
        metric_bold("Máximo de Artigos", int(df_serv['qtd'].max()) if not df_serv.empty else 0)

    st.markdown("---")

    st.subheader("Top 15 Servidores por Artigos Publicados")
    top_serv = df_serv.head(15).copy().sort_values('qtd', ascending=True)
    fig = px.bar(top_serv, x='qtd', y='servidor', orientation='h',
                 labels={'qtd': 'Artigos', 'servidor': 'Servidor'})
    fig.update_layout(height=600, showlegend=False, yaxis_title="")
    st.plotly_chart(fig, config={'responsive': True}, key="art_srv_top")

    st.markdown("---")

    st.subheader("Detalhes por Servidor")
    srv_sel = st.selectbox("Escolha um servidor", options=df_serv['servidor'].tolist())
    if srv_sel:
        df_prof = df[df['autores'] == srv_sel]
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total de Artigos", len(df_prof))
        with col_b:
            st.metric("Instituição", df_prof['instituicao'].mode().iloc[0] if not df_prof.empty else 'N/A')
        with col_c:
            st.metric("Veículos Distintos", df_prof['veiculo'].dropna().nunique())

        st.write("**Temas de Atuação:**")
        temas_prof = df_prof['nome_topico'].value_counts().head(5)
        for tema, count in temas_prof.items():
            st.write(f"• {simplificar_topico(tema)}: {count} artigos")

        if df_prof['veiculo'].notna().any():
            st.write("**Principais Veículos de Publicação:**")
            veiculos = df_prof['veiculo'].dropna().value_counts().head(5)
            for veiculo, count in veiculos.items():
                st.write(f"• {veiculo}: {count} artigos")

        st.write("**Evolução Temporal:**")
        df_tempo = df_prof.groupby('ano').size().reset_index(name='count')
        fig2 = px.line(df_tempo, x='ano', y='count', markers=True,
                       labels={'count': 'Artigos', 'ano': 'Ano'})
        fig2.update_layout(height=250, showlegend=False)
        st.plotly_chart(fig2, config={'responsive': True}, key="art_srv_tempo")

    st.markdown("---")

    st.subheader("Ranking Completo de Servidores")
    df_display = df_serv.copy()
    df_display['tema_simples'] = df_display['tema_principal'].apply(simplificar_topico)
    df_display = df_display[['servidor', 'qtd', 'instituicao', 'tema_simples']]
    df_display.columns = ['Servidor', 'Artigos', 'Instituição', 'Tema Principal']
    st.dataframe(df_display, hide_index=True, use_container_width=True, height=400)