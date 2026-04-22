# -*- coding: utf-8 -*-
import streamlit as st
import plotly.express as px
import pandas as pd
from utilitarios import metric_bold

# Mapeamento IF -> Estado -> UF
MAPA_IF_ESTADO = {
    'IFCE': 'CE', 'IFSP': 'SP', 'IFES': 'ES', 'IFMA': 'MA', 'IFPB': 'PB',
    'IFG': 'GO', 'IFMG': 'MG', 'IFRS': 'RS', 'IFC': 'SC', 'IFGOIANO': 'GO',
    'IFSC': 'SC', 'IFSULDEMINAS': 'MG', 'IFPI': 'PI', 'IFPR': 'PR',
    'IFRJ': 'RJ', 'IFRN': 'RN', 'IFFLUMINENSE': 'RJ', 'IFSUDESTEMG': 'MG',
    'IFTO': 'TO', 'IFSUL': 'RS', 'IFBA': 'BA', 'IFAL': 'AL', 'IFAM': 'AM',
    'IFAP': 'AP', 'IFMT': 'MT', 'IFMS': 'MS', 'IFPA': 'PA', 'IFPE': 'PE',
    'IFRR': 'RR', 'IFRO': 'RO', 'IFSE': 'SE', 'IFTM': 'MG', 'IFNMG': 'MG',
    'IFSERTAOPE': 'PE', 'IFBAIANO': 'BA', 'IFCATARINENSE': 'SC',
    'IFFAR': 'RS', 'IFPAMPA': 'RS', 'IFTRIANGULO': 'MG',
}

NOME_ESTADO = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AM': 'Amazonas', 'AP': 'Amapá',
    'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal',
    'ES': 'Espírito Santo', 'GO': 'Goiás', 'MA': 'Maranhão',
    'MG': 'Minas Gerais', 'MS': 'Mato Grosso do Sul', 'MT': 'Mato Grosso',
    'PA': 'Pará', 'PB': 'Paraíba', 'PE': 'Pernambuco', 'PI': 'Piauí',
    'PR': 'Paraná', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
    'RO': 'Rondônia', 'RR': 'Roraima', 'RS': 'Rio Grande do Sul',
    'SC': 'Santa Catarina', 'SE': 'Sergipe', 'SP': 'São Paulo',
    'TO': 'Tocantins', 'RR': 'Roraima',
}

def preparar_dados_estado(df):
    df = df.copy()
    df['uf'] = df['instituicao'].map(MAPA_IF_ESTADO)
    df_estado = df.groupby('uf').size().reset_index(name='quantidade')
    df_estado['estado'] = df_estado['uf'].map(NOME_ESTADO)
    df_estado = df_estado.dropna(subset=['uf'])
    return df_estado

def exibir(df_tcc, df_art, df_proj):
    st.subheader("🗺️ Mapa de Produção Acadêmica da Rede Federal")
    st.caption("Distribuição geográfica da produção por estado brasileiro")

    tipo = st.radio("Visualizar:", ["TCCs", "Artigos", "Projetos", "Total"],
                    horizontal=True)

    if tipo == "TCCs":
        df_map = preparar_dados_estado(df_tcc)
        cor = "Blues"
    elif tipo == "Artigos":
        df_map = preparar_dados_estado(df_art)
        cor = "Greens"
    elif tipo == "Projetos":
        df_map = preparar_dados_estado(df_proj)
        cor = "Oranges"
    else:
        df_tcc_e  = preparar_dados_estado(df_tcc).rename(columns={'quantidade': 'tcc'})
        df_art_e  = preparar_dados_estado(df_art).rename(columns={'quantidade': 'art'})
        df_proj_e = preparar_dados_estado(df_proj).rename(columns={'quantidade': 'proj'})
        df_map = df_tcc_e.merge(df_art_e[['uf','art']], on='uf', how='outer')
        df_map = df_map.merge(df_proj_e[['uf','proj']], on='uf', how='outer')
        df_map = df_map.fillna(0)
        df_map['quantidade'] = df_map['tcc'] + df_map['art'] + df_map['proj']
        df_map['quantidade'] = df_map['quantidade'].astype(int)
        cor = "Purples"

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_bold("Estados com produção", df_map['uf'].nunique())
    with col2:
        top_estado = df_map.loc[df_map['quantidade'].idxmax(), 'estado'] if not df_map.empty else 'N/A'
        metric_bold("Estado mais produtivo", top_estado)
    with col3:
        metric_bold("Total no mapa", f"{df_map['quantidade'].sum():,}".replace(",", "."))

    st.markdown("---")

    fig = px.choropleth(
        df_map,
        geojson="https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
        locations='estado',
        featureidkey="properties.name",
        color='quantidade',
        color_continuous_scale=cor,
        labels={'quantidade': 'Produção'},
        hover_data={'uf': True, 'quantidade': True, 'estado': True},
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=600, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, config={'responsive': True}, key="mapa_brasil", use_container_width=True)

    st.markdown("---")

    st.subheader("Ranking por Estado")
    df_rank = df_map.sort_values('quantidade', ascending=False)
    fig2 = px.bar(df_rank, x='estado', y='quantidade',
                  color='quantidade', color_continuous_scale=cor,
                  labels={'quantidade': 'Produção', 'estado': 'Estado'},
                  text='quantidade')
    fig2.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig2.update_layout(height=400, showlegend=False, xaxis_tickangle=-30,
                       xaxis_title="", yaxis_title="Quantidade", coloraxis_showscale=False)
    st.plotly_chart(fig2, config={'responsive': True}, key="mapa_ranking", use_container_width=True)