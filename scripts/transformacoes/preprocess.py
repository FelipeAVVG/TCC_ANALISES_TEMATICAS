# -*- coding: utf-8 -*-
"""
Script de Pré-processamento e Modelagem de Tópicos.

Esta versão lê TCCs, artigos e projetos já tratados no Data Mart ('datamart.db'),
gera um texto unificado por produção e executa a modelagem de tópicos para o dashboard.
"""

import sqlite3
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import time
from pathlib import Path
from unidecode import unidecode

# --- CONFIGURAÇÕES ---
PROCESSED_DB_NAME = "datamart.db"
# Mantido o mesmo nome para não quebrar a interface atual
OUTPUT_FILENAME = r"scripts\interface\producoes_dashboard.parquet"
N_TOPICS = 20

IGNORED_WORDS = set([
    # Conjunções, preposições e palavras comuns
    "apos", "atraves", "assim", "como", "com", "de", "da", "do", "dos", "das",
    "em", "e", "entre", "na", "no", "ou", "por", "sob", "sobre", "partir",
    "nao", "segundo", "dentro", "tendo", "ano", "anos",

    # Instituição, siglas e cargos
    "aluno", "alunos", "brasileira", "ciencia", "coorientacao", "faculdade",
    "if", "ifb", "ifba", "ifg", "ifgo", "instituicao", "instituto", "orientador",
    "pessoa", "professor", "sigla", "universidade", "tecnico", "publica", "federal",
    "secretariado", "popular", "estagio", "defesa", "analise",

    # Trabalho, documentação e produções acadêmicas
    "avaliacao", "conclusao", "conclusao_de_curso", "consideracoes",
    "dissertacao", "introducao", "metodologia", "objetivo", "objetivos",
    "palavra", "palavras", "projeto", "projetos", "referencias", "resumo",
    "tcc", "trabalho", "comparativo", "artigo", "artigos",

    # Termos genéricos de pesquisa
    "ensino", "medio", "curso", "superior", "educacao", "profissional",
    "docentes", "docencia", "abordagem", "aspectos", "base", "baseado",
    "banca", "caso", "cursos", "durante", "estrategia", "estrategias",
    "estudo", "eja", "ferramenta", "informacao", "informacoes",
    "licenciatura", "modelagem", "modelo", "modelos", "municipal", "novos",
    "pesquisa", "possiveis", "processo", "processos", "proposta", "propostas",
    "resultado", "tecnica", "tecnicas", "uso", "utilizacao", "usando",
    "perspectiva", "prof", "docente", "formacao", "pedagogica", "didatico",
    "metodos", "problemas", "resolucao", "tema", "sistema", "sistemas", "controle",

    # Termos administrativos e vagos
    "acerca", "acoes", "acesso", "alternativa", "aplicado", "areas",
    "biologia", "conceitos", "comparativa", "contribuicao", "contribuicoes",
    "contexto", "criancas", "deteccao", "diferentes", "dimensionamento", "elaboracao",
    "ensinoaprendizagem", "experiencia", "foco", "forma", "funcao", "impactos",
    "identificacao", "material", "melhoria", "novo", "novas", "periodo", "presente",
    "prototipo", "reflexoes", "relacoes", "representacao", "sequencia",
    "setor", "simulacao", "utilizando", "visao", "perspectivas", "indicadores", "livros",

    # Estados brasileiros e cidades
    "acre", "alagoas", "amapa", "amazonas", "anapolis", "aparecida", "bahia", "ceara",
    "cidade", "distrito", "espirito", "formosa", "goias", "goiania", "goianiago",
    "jatai", "joao", "maranhao", "mato", "minas", "para", "paraiba", "parana",
    "pernambuco", "piaui", "porto", "rio", "rondonia", "roraima", "salvador",
    "santa", "sergipe", "tocantins", "municipio", "brasil", "brasilia", "campus",
    "brasileiro", "sao", "paulo", "uruacu", "sul", "sudeste", "centrooeste",
    "norte", "nordeste", "federal", "centro", "oeste", "estadual"
])

# --- FUNÇÕES AUXILIARES ---

def setup_nltk():
    """Baixa as stopwords do NLTK se ainda não estiverem disponíveis."""
    try:
        stopwords.words("portuguese")
    except LookupError:
        print("--> Baixando recursos do NLTK (stopwords)...")
        nltk.download("stopwords")
        print("--> Download concluído.")


def clean_text_piece(value):
    """Normaliza pedaços de texto sem quebrar nulos."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).replace("&#10;", " ").strip()
    return re.sub(r"\s+", " ", text)


def preprocess_text(text):
    """Limpa e normaliza o texto para o modelo, ignorando palavras irrelevantes."""
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = unidecode(text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = text.split()
    stop_words = set(stopwords.words("portuguese"))

    tokens = [
        word for word in tokens
        if len(word) > 2 and word not in stop_words and word not in IGNORED_WORDS
    ]
    return " ".join(tokens)


def get_topic_name(topic_idx, top_words):
    """Cria um nome de tópico legível a partir de suas palavras-chave."""
    capitalized_words = [word.capitalize() for word in top_words]
    return f"Tópico {topic_idx}: {', '.join(capitalized_words)}"


def montar_texto_analise(row):
    """Monta o texto-base da análise conforme o tipo de produção."""
    tipo = row.get("tipo", "")
    partes = [clean_text_piece(row.get("titulo"))]

    if tipo == "TCC":
        partes.extend([
            clean_text_piece(row.get("resumo")),
            clean_text_piece(row.get("palavras_chaves")),
            clean_text_piece(row.get("curso")),
        ])
    elif tipo == "Artigo":
        partes.extend([
            clean_text_piece(row.get("veiculo")),
            clean_text_piece(row.get("palavras_chaves")),
        ])
    elif tipo == "Projeto":
        partes.extend([
            clean_text_piece(row.get("resumo")),
            clean_text_piece(row.get("natureza")),
            clean_text_piece(row.get("financiadores")),
        ])
    else:
        partes.extend([
            clean_text_piece(row.get("resumo")),
            clean_text_piece(row.get("palavras_chaves")),
        ])

    texto = " ".join([parte for parte in partes if parte])
    return re.sub(r"\s+", " ", texto).strip()


def escolher_parametros_modelagem(total_docs):
    """Ajusta parâmetros para evitar erro com bases pequenas."""
    if total_docs < 50:
        return {"min_df": 1, "max_df": 1.0, "max_features": 1000}
    if total_docs < 300:
        return {"min_df": 2, "max_df": 0.95, "max_features": 1500}
    if total_docs < 1000:
        return {"min_df": 5, "max_df": 0.92, "max_features": 2000}
    return {"min_df": 20, "max_df": 0.90, "max_features": 2500}


def load_data_from_datamart(db_name):
    """Carrega e junta TCCs, artigos e projetos do Data Mart em uma visão plana."""
    print(f"1. Carregando dados do Data Mart '{db_name}'...")

    try:
        with sqlite3.connect(db_name) as conn:
            # TCCs
            query_tcc = """
                SELECT
                    t.tcc_id AS registro_id,
                    t.titulo,
                    t.resumo,
                    t.ano,
                    i.sigla AS instituicao,
                    c.nome_curso AS curso,
                    GROUP_CONCAT(p_aluno.nome_pessoa) AS autores,
                    p_orientador.nome_pessoa AS orientador,
                    t.palavras_chaves,
                    NULL AS natureza,
                    NULL AS financiadores,
                    NULL AS veiculo,
                    'TCC' AS tipo
                FROM fato_tcc t
                LEFT JOIN dim_instituicao i ON t.instituicao_id = i.instituicao_id
                LEFT JOIN dim_curso c ON t.curso_id = c.curso_id
                LEFT JOIN ponte_tcc_aluno pta ON t.tcc_id = pta.tcc_id
                LEFT JOIN dim_pessoa p_aluno ON pta.aluno_id = p_aluno.pessoa_id
                LEFT JOIN ponte_tcc_orientador pto ON t.tcc_id = pto.tcc_id
                LEFT JOIN dim_pessoa p_orientador ON pto.orientador_id = p_orientador.pessoa_id
                GROUP BY t.tcc_id
            """
            df_tcc = pd.read_sql_query(query_tcc, conn)

            # Artigos
            try:
                query_art = """
                    SELECT
                        a.artigo_id AS registro_id,
                        a.titulo,
                        '' AS resumo,
                        a.ano,
                        COALESCE(i.sigla, a.sigla) AS instituicao,
                        NULL AS curso,
                        a.nome_professor AS autores,
                        NULL AS orientador,
                        a.palavras_chaves,
                        NULL AS natureza,
                        NULL AS financiadores,
                        a.journal AS veiculo,
                        'Artigo' AS tipo
                    FROM fato_artigo a
                    LEFT JOIN dim_instituicao i ON a.sigla = i.sigla
                """
                df_art = pd.read_sql_query(query_art, conn)
            except Exception:
                df_art = pd.DataFrame()

            # Projetos
            try:
                query_proj = """
                    SELECT
                        p.projeto_id AS registro_id,
                        p.titulo,
                        p.descricao AS resumo,
                        NULL AS ano,
                        COALESCE(i.sigla, p.sigla) AS instituicao,
                        NULL AS curso,
                        p.nome_professor AS autores,
                        NULL AS orientador,
                        NULL AS palavras_chaves,
                        p.natureza,
                        p.financiadores,
                        NULL AS veiculo,
                        'Projeto' AS tipo
                    FROM fato_projeto p
                    LEFT JOIN dim_instituicao i ON p.sigla = i.sigla
                """
                df_proj = pd.read_sql_query(query_proj, conn)
            except Exception:
                df_proj = pd.DataFrame()

        print(f"   - {len(df_tcc)} registros de TCC carregados.")
        if not df_art.empty:
            print(f"   - {len(df_art)} registros de artigos carregados.")
        if not df_proj.empty:
            print(f"   - {len(df_proj)} registros de projetos carregados.")

        frames = [df_tcc]
        if not df_art.empty:
            frames.append(df_art)
        if not df_proj.empty:
            frames.append(df_proj)

        df = pd.concat(frames, ignore_index=True)
        return df

    except Exception as e:
        print(f"   - ERRO AO CARREGAR DADOS: {e}")
        return None


# --- FUNÇÃO PRINCIPAL ---

def main():
    """Função principal que orquestra todo o processo."""
    print("\n--- Iniciando script preprocess.py ---")
    start_time = time.time()

    setup_nltk()
    df = load_data_from_datamart(PROCESSED_DB_NAME)

    if df is None or df.empty:
        print("\nProcesso interrompido. Verifique se o 'datamart.db' foi gerado corretamente.")
        return

    print("2. Realizando pré-processamento dos textos...")
    df["texto_completo"] = df.apply(montar_texto_analise, axis=1)
    df["resumo_processado"] = df["texto_completo"].apply(preprocess_text)

    df.dropna(subset=["resumo_processado"], inplace=True)
    df = df[df["resumo_processado"].astype(str).str.strip() != ""]
    print(f"   - {len(df)} registros restantes após limpeza.")

    if df.empty:
        print("   - Nenhum texto válido restou após o pré-processamento.")
        return

    print("3. Executando Modelagem de Tópicos (LDA)...")
    params = escolher_parametros_modelagem(len(df))
    print(
        f"   - Parâmetros do vetor: min_df={params['min_df']}, "
        f"max_df={params['max_df']}, max_features={params['max_features']}"
    )

    try:
        vectorizer = CountVectorizer(
            max_df=params["max_df"],
            min_df=params["min_df"],
            max_features=params["max_features"],
            ngram_range=(1, 2)
        )
        X = vectorizer.fit_transform(df["resumo_processado"])
    except ValueError:
        print("   - Ajustando parâmetros para base menor/mais esparsa...")
        vectorizer = CountVectorizer(
            max_df=1.0,
            min_df=1,
            max_features=1000,
            ngram_range=(1, 1)
        )
        X = vectorizer.fit_transform(df["resumo_processado"])

    if X.shape[0] == 0 or X.shape[1] == 0:
        print("   - Não foi possível gerar vocabulário para a modelagem.")
        return

    n_topics_real = max(1, min(N_TOPICS, X.shape[0], X.shape[1]))
    print(f"   - Número de tópicos utilizado: {n_topics_real}")

    lda = LatentDirichletAllocation(
        n_components=n_topics_real,
        random_state=42,
        n_jobs=-1
    )
    topic_results = lda.fit_transform(X)
    print("   - Modelagem concluída.")

    print("4. Gerando nomes interpretáveis para os temas...")
    feature_names = vectorizer.get_feature_names_out()
    topic_name_mapping = {}
    for topic_idx, topic_component in enumerate(lda.components_):
        top_words = [feature_names[i] for i in topic_component.argsort()[:-4:-1]]
        topic_name = get_topic_name(topic_idx, top_words)
        topic_name_mapping[topic_idx] = topic_name
        print(f"   - {topic_name}")

    print("5. Atribuindo o tema principal a cada produção...")
    df["id_topico"] = topic_results.argmax(axis=1)
    df["nome_topico"] = df["id_topico"].map(topic_name_mapping)
    print("   - Atribuição concluída.")

    print(f"6. Salvando o DataFrame enriquecido em '{OUTPUT_FILENAME}'...")
    output_path = Path(OUTPUT_FILENAME)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df_final = df[
        [
            "registro_id",
            "tipo",
            "titulo",
            "autores",
            "ano",
            "instituicao",
            "curso",
            "veiculo",
            "resumo",
            "palavras_chaves",
            "natureza",
            "financiadores",
            "texto_completo",
            "resumo_processado",
            "nome_topico",
            "orientador",
        ]
    ].copy()

    df_final.to_parquet(output_path, index=False)
    print("   - Arquivo salvo com sucesso!")

    end_time = time.time()
    print(f"\n--- Processo finalizado em {end_time - start_time:.2f} segundos. ---")


if __name__ == "__main__":
    main()
