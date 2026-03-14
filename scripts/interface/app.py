# -*- coding: utf-8 -*-
import streamlit as st

# Importações dos módulos locais (arquivos dentro de scripts/interface/)
from dados import carregar_dados
from utilitarios import filtrar_dados
from estilo import aplicar_estilo

import visao_geral
import orientadores
import instituicoes
import tematicas
import busca_avancada
import tendencias

# Configuração da página
st.set_page_config(
    page_title="Panorama Temático de TCCs",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar o estilo que foi definido no script estilo.py
aplicar_estilo()

# Carregar os dados usando a função presente no dados.py
with st.spinner("🚀 Carregando o projeto e preparando os dados..."):
    df = carregar_dados()

# Definindo o header
st.markdown("""
<div class="main-header">
    <h1>Panorama Temático de TCCs na Rede Federal</h1>
    <p style='margin: 5px 0 0 0; font-size: 1.1em;'>Análise Inteligente de Trabalhos de Conclusão de Curso</p>
</div>
""", unsafe_allow_html=True)

# Filtros adicionados no menu lateral
with st.sidebar:
    st.header("Filtros")
    ano_min = int(df['ano'].min())
    ano_max = int(df['ano'].max())
    anos = st.slider("Período", min_value=ano_min, max_value=ano_max, value=(ano_min, ano_max))
    inst = st.multiselect("Instituições", options=sorted(df['instituicao'].dropna().unique()))
    cursos = st.multiselect("Cursos", options=sorted(df['curso_unificado'].dropna().unique()))
    topicos = st.multiselect("Temas", options=sorted(df['nome_topico'].dropna().unique()))
    tipos = st.multiselect("Tipo de registro", options=sorted(df['tipo'].dropna().unique()), default=sorted(df['tipo'].dropna().unique()))

# Aplicar filtro utilizando a função filtrar_dados que foi definida no utilitarios.py
df_filtrado = filtrar_dados(df, inst, anos, topicos, cursos, tipos)

# Caso não seja encontrado nenhum dado para o filtro feito deve ser apresentado uma mensagem
if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados. Ajuste os filtros na lateral.")
    st.stop()

# Bloco de CSS customizado para estilizar as abas do menu
st.markdown("""
<style>
    /* Estiliza cada aba individualmente */
    button[data-baseweb="tab"] {
        font-weight: bold;
        padding: 10px 15px;
        margin-right: 10px;
        border-radius: 8px 8px 8px 8px;
        background-color: #F0F2F6;
        border-bottom: 2px solid transparent;
    }
</style>
""", unsafe_allow_html=True)

# Menu superior referente as visualizações
abas = st.tabs([
    "Visão Geral",
    "Orientadores",
    "Instituições",
    "Temáticas",
    "Busca Avançada",
    "Tendências"
])

# Renderizar cada aba seguindo os dados filtrados
with abas[0]:
    visao_geral.exibir(df_filtrado)

with abas[1]:
    orientadores.exibir(df_filtrado)

with abas[2]:
    instituicoes.exibir(df_filtrado)

with abas[3]:
    tematicas.exibir(df_filtrado)

with abas[4]:
    busca_avancada.exibir(df_filtrado)

with abas[5]:
    tendencias.exibir(df_filtrado)

# Rodapé
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Dashboard de Trabalhos de Conclusão de Curso da Rede Federal</strong></p>
    <p>Desenvolvido por Ana Luísa Caixeta - 2025</p>
</div>
""", unsafe_allow_html=True)
