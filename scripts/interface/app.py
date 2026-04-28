
# # -*- coding: utf-8 -*-
# import streamlit as st
# from dados import carregar_dados
# from utilitarios import filtrar_dados
# from estilo import aplicar_estilo

# # Módulos TCC (originais, sem alteração)
# import visao_geral
# import orientadores
# import instituicoes
# import tematicas
# import busca_avancada
# import tendencias

# # Módulos Artigos
# import artigos_visao_geral
# import artigos_tematicas
# import artigos_instituicoes
# import artigos_busca
# import artigos_tendencias

# # Módulos Projetos (reusa os de artigos com o mesmo df)
# import projetos_visao_geral
# import projetos_tematicas
# import projetos_instituicoes
# import projetos_busca
# import projetos_tendencias

# st.set_page_config(
#     page_title="Panorama Temático de TCCs",
#     page_icon="📚",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# aplicar_estilo()

# st.markdown("""
# <style>
#     .block-container {
#         padding-top: 1rem !important;
#         margin-top: 0rem !important;
#     }
#     header[data-testid="stHeader"] {
#         height: 0rem;
#         visibility: hidden;
#     }
# </style>
# """, unsafe_allow_html=True)

# # ── NAVEGAÇÃO PRINCIPAL ───────────────────────────────────────────────────────
# tipo_selecionado = st.segmented_control(
#     label="Base de dados",
#     options=["📊 Dados Gerais", "📚 TCCs", "🔬 Artigos", "🗂️ Projetos"],
#     default="📊 Dados Gerais",
#     label_visibility="collapsed"
# )


# PARQUET_MAP = {
#     "📚 TCCs":        "tccs_dashboard.parquet",
#     "🔬 Artigos":     "artigos_dashboard.parquet",
#     "🗂️ Projetos":    "projetos_dashboard.parquet",
# }

# with st.spinner("🚀 Carregando o projeto e preparando os dados..."):
#     if tipo_selecionado == "📊 Dados Gerais":
#         df_tcc  = carregar_dados("tccs_dashboard.parquet")
#         df_art  = carregar_dados("artigos_dashboard.parquet")
#         df_proj = carregar_dados("projetos_dashboard.parquet")
#         df = df_tcc
#     else:
#         df = carregar_dados(PARQUET_MAP[tipo_selecionado])

# # ── BANNER ────────────────────────────────────────────────────────────────────
# TITULOS = {
#     "📊 Dados Gerais": ("Panorama da Produção Acadêmica na Rede Federal", "Análise Comparativa de TCCs, Artigos e Projetos"),
#     "📚 TCCs":         ("Panorama Temático de TCCs na Rede Federal",      "Análise Inteligente de Trabalhos de Conclusão de Curso"),
#     "🔬 Artigos":      ("Panorama de Artigos Científicos na Rede Federal", "Análise Inteligente de Artigos Científicos"),
#     "🗂️ Projetos":     ("Panorama de Projetos Acadêmicos na Rede Federal", "Análise Inteligente de Projetos Acadêmicos"),
# }

# titulo, subtitulo = TITULOS[tipo_selecionado]
# st.markdown(f"""
# <div class="main-header">
#     <h1>{titulo}</h1>
#     <p style='margin: 5px 0 0 0; font-size: 1.1em;'>{subtitulo}</p>
# </div>
# """, unsafe_allow_html=True)

# # ── FILTROS LATERAIS ──────────────────────────────────────────────────────────
# with st.sidebar:
#     st.header("Filtros")

#     anos = None
#     cursos = []
#     tipos = []
#     topicos = []
#     inst = []

#     if tipo_selecionado != "📊 Dados Gerais":
#         inst = st.multiselect("Instituições", options=sorted(df['instituicao'].dropna().unique()))
#         topicos = st.multiselect("Temas", options=sorted(df['nome_topico'].dropna().unique()))

#         if tipo_selecionado != "🗂️ Projetos":
#             ano_min = int(df['ano'].min())
#             ano_max = int(df['ano'].max())
#             anos = st.slider("Período", min_value=ano_min, max_value=ano_max, value=(ano_min, ano_max))

#         if tipo_selecionado == "📚 TCCs":
#             cursos = st.multiselect("Cursos", options=sorted(df['curso_unificado'].dropna().unique()))
#             tipos = st.multiselect("Tipo de registro", options=sorted(df['tipo'].dropna().unique()), default=sorted(df['tipo'].dropna().unique()))

# # ── FILTRAR ───────────────────────────────────────────────────────────────────
# if tipo_selecionado == "📊 Dados Gerais":
#     df_filtrado = df_tcc
# else:
#     df_filtrado = filtrar_dados(df, inst, anos if anos else (0, 9999), topicos, cursos, tipos)

# # ── CSS ABAS ──────────────────────────────────────────────────────────────────
# st.markdown("""
# <style>
#     button[data-baseweb="tab"] {
#         font-weight: bold;
#         padding: 10px 15px;
#         margin-right: 10px;
#         border-radius: 8px 8px 8px 8px;
#         background-color: #F0F2F6;
#         border-bottom: 2px solid transparent;
#     }
# </style>
# """, unsafe_allow_html=True)

# # ── ABAS POR TIPO ─────────────────────────────────────────────────────────────
# if tipo_selecionado == "📚 TCCs":
#     abas = st.tabs(["Visão Geral", "Orientadores", "Instituições", "Temáticas", "Busca Avançada", "Tendências"])
#     with abas[0]: visao_geral.exibir(df_filtrado)
#     with abas[1]: orientadores.exibir(df_filtrado)
#     with abas[2]: instituicoes.exibir(df_filtrado)
#     with abas[3]: tematicas.exibir(df_filtrado)
#     with abas[4]: busca_avancada.exibir(df_filtrado)
#     with abas[5]: tendencias.exibir(df_filtrado)

# elif tipo_selecionado == "🔬 Artigos":
#     import artigos_servidores
#     abas = st.tabs(["Visão Geral", "Temáticas", "Instituições", "Servidores", "Busca", "Tendências"])
#     with abas[0]: artigos_visao_geral.exibir(df_filtrado)
#     with abas[1]: artigos_tematicas.exibir(df_filtrado)
#     with abas[2]: artigos_instituicoes.exibir(df_filtrado)
#     with abas[3]: artigos_servidores.exibir(df_filtrado)
#     with abas[4]: artigos_busca.exibir(df_filtrado)
#     with abas[5]: artigos_tendencias.exibir(df_filtrado)

# elif tipo_selecionado == "🗂️ Projetos":
#     import projetos_servidores
#     abas = st.tabs(["Visão Geral", "Temáticas", "Instituições", "Servidores", "Busca", "Tendências"])
#     with abas[0]: projetos_visao_geral.exibir(df_filtrado)
#     with abas[1]: projetos_tematicas.exibir(df_filtrado)
#     with abas[2]: projetos_instituicoes.exibir(df_filtrado)
#     with abas[3]: projetos_servidores.exibir(df_filtrado)
#     with abas[4]: projetos_busca.exibir(df_filtrado)
#     with abas[5]: projetos_tendencias.exibir(df_filtrado)

# elif tipo_selecionado == "📊 Dados Gerais":
#     abas_dg = st.tabs(["Visão Geral", "Temáticas", "Servidores", "Mapa"])
#     with abas_dg[0]:
#         import comparacoes
#         comparacoes.exibir(df_tcc, df_art, df_proj)
#     with abas_dg[1]:
#         import dados_gerais_tematicas
#         dados_gerais_tematicas.exibir(df_tcc, df_art, df_proj)
#     with abas_dg[2]:
#         import dados_gerais_servidores
#         dados_gerais_servidores.exibir(df_tcc, df_art, df_proj)
#     with abas_dg[3]:
#         import mapa
#         mapa.exibir(df_tcc, df_art, df_proj)

# # ── RODAPÉ ────────────────────────────────────────────────────────────────────
# st.markdown("---")
# st.markdown("""
# <div style='text-align: center; color: #666; padding: 20px;'>
#     <p><strong>Dashboard de Trabalhos de Conclusão de Curso da Rede Federal</strong></p>
#     <p>Desenvolvido por Ana Luísa Caixeta, Anna Caroline Ribeiro, Felipe Gomes e Geovana Perazzo</p>
# </div>
# """, unsafe_allow_html=True)

# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
import requests

# IDs do Google Drive
DRIVE_IDS = {
    "artigos_dashboard.parquet":  "1PFgyctCUeMIeIaWQhk5VJa1_yVSnuC1z",
    "projetos_dashboard.parquet": "1Inic8ZfwcOV5QE-DfwezmBp5lxgX1xao",
    "tccs_dashboard.parquet":     "18esmAZm20GFo-PNLzXurUJ4ycwO4sGAE",
}

COLUNAS_OBRIGATORIAS = {
    "tccs_dashboard.parquet":     ['titulo', 'autores', 'ano', 'instituicao', 'resumo', 'resumo_processado', 'curso', 'nome_topico', 'orientador', 'curso_unificado', 'tipo'],
    "artigos_dashboard.parquet":  ['titulo', 'autores', 'ano', 'instituicao', 'resumo', 'resumo_processado', 'nome_topico', 'orientador', 'tipo'],
    "projetos_dashboard.parquet": ['titulo', 'autores', 'instituicao', 'resumo', 'resumo_processado', 'nome_topico', 'tipo'],
}

def baixar_do_drive(file_id, destino):
    """Baixa arquivo do Google Drive pelo ID."""
    URL = "https://drive.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params={"id": file_id}, stream=True)

    # Lida com arquivos grandes (confirmação de vírus)
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            response = session.get(URL, params={"id": file_id, "confirm": value}, stream=True)
            break

    with open(destino, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk:
                f.write(chunk)

@st.cache_data
def carregar_dados(nome_arquivo="tccs_dashboard.parquet"):
    try:
        # Tenta carregar do disco local primeiro
        BASE_DIR = os.path.dirname(__file__)
        file_path = os.path.join(BASE_DIR, nome_arquivo)

        if not os.path.exists(file_path):
            # Baixa do Google Drive se não existir localmente
            file_id = DRIVE_IDS.get(nome_arquivo)
            if not file_id:
                st.error(f"ID do Google Drive não configurado para '{nome_arquivo}'.")
                st.stop()
            with st.spinner(f"⬇️ Baixando {nome_arquivo} do Google Drive..."):
                baixar_do_drive(file_id, file_path)

        df = pd.read_parquet(file_path)

        required_cols = COLUNAS_OBRIGATORIAS.get(nome_arquivo, [])
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Colunas faltando em '{nome_arquivo}': {missing}")
            st.stop()

        # Normalizar ano
        if 'ano' in df.columns:
            df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
            df_com_ano = df.dropna(subset=['ano'])
            if not df_com_ano.empty:
                df = df_com_ano
                df['ano'] = df['ano'].astype(int)

        if df.empty:
            st.error(f"Nenhum registro válido encontrado em '{nome_arquivo}'.")
            st.stop()

        return df

    except FileNotFoundError:
        st.error(f"Arquivo '{nome_arquivo}' não encontrado.")
        st.stop()

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.stop()