
# -*- coding: utf-8 -*-
import streamlit as st
from dados import carregar_dados
from utilitarios import filtrar_dados
from estilo import aplicar_estilo

# Módulos TCC (originais, sem alteração)
import visao_geral
import orientadores
import instituicoes
import tematicas
import busca_avancada
import tendencias

# Módulos Artigos
import artigos_visao_geral
import artigos_tematicas
import artigos_instituicoes
import artigos_busca
import artigos_tendencias

# Módulos Projetos (reusa os de artigos com o mesmo df)
import projetos_visao_geral
import projetos_tematicas
import projetos_instituicoes
import projetos_busca
import projetos_tendencias

st.set_page_config(
    page_title="Panorama Temático de TCCs",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

aplicar_estilo()


# ── NAVEGAÇÃO PRINCIPAL ───────────────────────────────────────────────────────
tipo_selecionado = st.segmented_control(
    label="Base de dados",
    options=["📚 TCCs", "🔬 Artigos", "🗂️ Projetos", "📊 Comparações", "🗺️ Mapa"],
    default="📚 TCCs",
    label_visibility="collapsed"
)



PARQUET_MAP = {
    "📚 TCCs":     "tccs_dashboard.parquet",
    "🔬 Artigos":  "artigos_dashboard.parquet",
    "🗂️ Projetos": "projetos_dashboard.parquet",
}

with st.spinner("🚀 Carregando o projeto e preparando os dados..."):
    if tipo_selecionado in ["📊 Comparações", "🗺️ Mapa"]:
        df_tcc  = carregar_dados("tccs_dashboard.parquet")
        df_art  = carregar_dados("artigos_dashboard.parquet")
        df_proj = carregar_dados("projetos_dashboard.parquet")
        df = df_tcc
    else:
        df = carregar_dados(PARQUET_MAP[tipo_selecionado])

# ── BANNER ────────────────────────────────────────────────────────────────────
TITULOS = {
    "📚 TCCs":         ("Panorama Temático de TCCs na Rede Federal",      "Análise Inteligente de Trabalhos de Conclusão de Curso"),
    "🔬 Artigos":      ("Panorama de Artigos Científicos na Rede Federal", "Análise Inteligente de Artigos Científicos"),
    "🗂️ Projetos":     ("Panorama de Projetos Acadêmicos na Rede Federal", "Análise Inteligente de Projetos Acadêmicos"),
    "📊 Comparações":  ("Comparações entre TCCs, Artigos e Projetos",      "Análise Comparativa da Produção Acadêmica na Rede Federal"),
    "🗺️ Mapa": ("Mapa de Produção Acadêmica da Rede Federal", "Distribuição Geográfica por Estado"),
}
titulo, subtitulo = TITULOS[tipo_selecionado]
st.markdown(f"""
<div class="main-header">
    <h1>{titulo}</h1>
    <p style='margin: 5px 0 0 0; font-size: 1.1em;'>{subtitulo}</p>
</div>
""", unsafe_allow_html=True)

# ── FILTROS LATERAIS ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filtros")
    inst = st.multiselect("Instituições", options=sorted(df['instituicao'].dropna().unique()))
    topicos = st.multiselect("Temas", options=sorted(df['nome_topico'].dropna().unique()))

    anos = None
    cursos = []
    tipos = []

    if tipo_selecionado != "🗂️ Projetos":
        ano_min = int(df['ano'].min())
        ano_max = int(df['ano'].max())
        anos = st.slider("Período", min_value=ano_min, max_value=ano_max, value=(ano_min, ano_max))

    if tipo_selecionado == "📚 TCCs":
        cursos = st.multiselect("Cursos", options=sorted(df['curso_unificado'].dropna().unique()))
        tipos = st.multiselect("Tipo de registro", options=sorted(df['tipo'].dropna().unique()), default=sorted(df['tipo'].dropna().unique()))
# ── FILTRAR ───────────────────────────────────────────────────────────────────
df_filtrado = filtrar_dados(df, inst, anos if anos else (0, 9999), topicos, cursos, tipos)

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados. Ajuste os filtros na lateral.")
    st.stop()

# ── CSS ABAS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
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

# ── ABAS POR TIPO ─────────────────────────────────────────────────────────────
if tipo_selecionado == "📚 TCCs":
    abas = st.tabs(["Visão Geral", "Orientadores", "Instituições", "Temáticas", "Busca Avançada", "Tendências"])
    with abas[0]: visao_geral.exibir(df_filtrado)
    with abas[1]: orientadores.exibir(df_filtrado)
    with abas[2]: instituicoes.exibir(df_filtrado)
    with abas[3]: tematicas.exibir(df_filtrado)
    with abas[4]: busca_avancada.exibir(df_filtrado)
    with abas[5]: tendencias.exibir(df_filtrado)

elif tipo_selecionado == "🔬 Artigos":
    abas = st.tabs(["Visão Geral", "Temáticas", "Instituições", "Busca", "Tendências"])
    with abas[0]: artigos_visao_geral.exibir(df_filtrado)
    with abas[1]: artigos_tematicas.exibir(df_filtrado)
    with abas[2]: artigos_instituicoes.exibir(df_filtrado)
    with abas[3]: artigos_busca.exibir(df_filtrado)
    with abas[4]: artigos_tendencias.exibir(df_filtrado)

elif tipo_selecionado == "🗂️ Projetos":
    abas = st.tabs(["Visão Geral", "Temáticas", "Instituições", "Busca", "Tendências"])
    with abas[0]: projetos_visao_geral.exibir(df_filtrado)
    with abas[1]: projetos_tematicas.exibir(df_filtrado)
    with abas[2]: projetos_instituicoes.exibir(df_filtrado)
    with abas[3]: projetos_busca.exibir(df_filtrado)
    with abas[4]: projetos_tendencias.exibir(df_filtrado)

elif tipo_selecionado == "📊 Comparações":
    import comparacoes
    comparacoes.exibir(df_tcc, df_art, df_proj)

elif tipo_selecionado == "🗺️ Mapa":
    import mapa
    mapa.exibir(df_tcc, df_art, df_proj)

# ── RODAPÉ ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Dashboard de Trabalhos de Conclusão de Curso da Rede Federal</strong></p>
    <p>Desenvolvido por Ana Luísa Caixeta - 2025</p>
</div>
""", unsafe_allow_html=True)