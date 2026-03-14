# C:\...\extracao\scraper.py

import asyncio
import aiohttp
import time
from datetime import datetime

import config  # Importação direta
from database import DatabaseManager, clean_value # Importação direta

def log(msg):
    """Função simples de log com timestamp."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# O restante do código deste arquivo permanece exatamente o mesmo da resposta anterior...
# (fetch_professores, _fetch_detail, fetch_detalhes, run_for_institution)

# Toggle para logar apenas uma vez a ausência/estrutura de projetos
_projetos_debug_logged = False

async def fetch_professores(sigla, base_url, db_manager, progress_callback=None):
    """Busca a lista de todos os professores de uma instituição."""
    list_url = f"{base_url}/api/portfolio/pessoa/data"
    professores = []
    start = 0
    total = 1

    if progress_callback:
        progress_callback(0, "?")

    async with aiohttp.ClientSession() as session:
        while True:
            params = {"start": start, "length": config.PAGE_SIZE}
            try:
                async with session.get(list_url, params=params, headers=config.DEFAULT_HEADERS, ssl=False) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
            except Exception as e:
                log(f"[{sigla}] Erro ao buscar lista de professores (start={start}): {e}")
                break

            if not isinstance(data, list) or len(data) < 2 or not data[1]:
                break

            meta, batch = data[0] or {}, data[1] or []
            total = meta.get("total", total)
            length_returned = meta.get("length", len(batch)) or len(batch)

            for p in batch:
                if slug := p.get("slug"):
                    professores.append({
                        "nome": p.get("nome"),
                        "campus": p.get("campusNome"),
                        "cargo": p.get("cargo"),
                        "slug": slug,
                        "url_final": f"{base_url}/portfolio/pessoas/{slug}",
                    })
            
            log(f"[{sigla}] [{len(professores)}/{total}] - professores coletados")
            if progress_callback:
                progress_callback(len(professores), total)

            if len(professores) >= total:
                break
            
            start += length_returned
            await asyncio.sleep(0.05)

    if professores:
        db_manager.save_professores(sigla, professores)
    return professores

async def _fetch_detail(session, detail_url, p):
    """Função auxiliar para buscar o detalhe de um único professor.

    Implementa retry simples em caso de 429 (rate limit) e registra o tempo total.
    """
    slug = p["slug"]
    start_time = time.perf_counter()

    max_retries = 3
    backoff_base = 1.0

    for attempt in range(1, max_retries + 1):
        try:
            async with session.get(f"{detail_url}/{slug}", headers=config.DEFAULT_HEADERS, ssl=False) as resp:
                if resp.status == 429:
                    # Rate limit; respeita Retry-After se presente
                    retry_after = resp.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after and retry_after.isdigit() else backoff_base * attempt
                    log(f"[{p.get('sigla')}] 429 rate limit para {slug} (tentativa {attempt}/{max_retries}), aguardando {delay:.1f}s")
                    await asyncio.sleep(delay)
                    continue

                if resp.status >= 400:
                    elapsed = time.perf_counter() - start_time
                    return slug, p, {"erro": f"HTTP {resp.status}"}, elapsed

                data = await resp.json()
                elapsed = time.perf_counter() - start_time
                return slug, p, data, elapsed

        except Exception as e:
            # Em caso de exceções de rede, tenta novamente até max_retries
            if attempt == max_retries:
                elapsed = time.perf_counter() - start_time
                return slug, p, {"erro": str(e)}, elapsed
            await asyncio.sleep(backoff_base * attempt)

    elapsed = time.perf_counter() - start_time
    return slug, p, {"erro": "Max retries exceeded"}, elapsed

async def fetch_detalhes(sigla, base_url, uf, professores, db_manager, progress_callback=None, progress_callback_art=None):
    """Busca os detalhes (TCCs, artigos e projetos) para uma lista de professores."""
    if not professores:
        log(f"[{sigla}] Nenhum professor para buscar detalhes.")
        return

    detail_url = f"{base_url}/api/portfolio/pessoa/s"
    connector = aiohttp.TCPConnector(limit=config.MAX_CONCURRENT)
    completed = 0
    total = len(professores)
    art_count = 0
    proj_count = 0

    log(f"[{sigla}] Coletando detalhes de {total} professores...")
    if progress_callback:
        progress_callback(0, total)
    if progress_callback_art:
        progress_callback_art(0, "?")

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [_fetch_detail(session, detail_url, {**p, "sigla": sigla}) for p in professores]
        
        for coro in asyncio.as_completed(tasks):
            slug, prof, data, elapsed = await coro
            completed += 1
            
            log(f"[{sigla}] [{completed}/{total}] - {slug} -> {elapsed:.2f}s")
            if progress_callback:
                progress_callback(completed, total)

            tccs_para_salvar = []
            artigos_para_salvar = []
            projetos_para_salvar = []

            # orientações / TCCs
            outra_producao = data.get("outraProducao", {})
            if isinstance(outra_producao, dict) and "orientacoesConcluidas" in outra_producao:
                for item in outra_producao.get("orientacoesConcluidas", []):
                    for trabalho in item.get("outrasOrientacoesConcluidas", []):
                        dados_basicos = trabalho.get("dadosBasicosDeOutrasOrientacoesConcluidas", {})
                        if dados_basicos.get("natureza") != "TRABALHO_DE_CONCLUSAO_DE_CURSO_GRADUACAO":
                            continue

                        detalhamento = trabalho.get("detalhamentoDeOutrasOrientacoesConcluidas", {})
                        nome_professor = clean_value(prof.get("nome"))
                        autores = clean_value(detalhamento.get("nomeDoOrientado"))
                        if nome_professor:
                            autores = (autores + ", " if autores else "") + f"{nome_professor} (Orientador/a)"

                        palavras = trabalho.get("palavrasChave") or {}
                        info_add = trabalho.get("informacoesAdicionais") or {}

                        tccs_para_salvar.append((
                            slug, nome_professor, prof.get("sigla"),
                            clean_value(detalhamento.get("nomeDaInstituicao")), uf, clean_value(prof.get("campus")),
                            clean_value(dados_basicos.get("ano")), clean_value(detalhamento.get("nomeDoCurso")),
                            autores, clean_value(dados_basicos.get("titulo")),
                            clean_value(info_add.get("descricaoInformacoesAdicionais")),
                            clean_value(palavras.get("palavrasChaves"))
                        ))

            # artigos científicos
            prodbib = data.get("producaoBibliografica", {})
            if isinstance(prodbib, dict):
                for bloco in prodbib.get("artigosPublicados", []):
                    for art in bloco.get("artigoPublicado", []):
                        dados = art.get("dadosBasicosDoArtigo", {})
                        titulo_art = dados.get("tituloDoArtigo") or dados.get("titulo")
                        ano_art = dados.get("anoDoArtigo") or dados.get("ano")
                        palavras = art.get("palavrasChave") or {}
                        journal = art.get("detalhamentoDoArtigo", {}).get("tituloDoPeriodicoOuRevista")
                        doi = dados.get("doi")
                        nome_professor = clean_value(prof.get("nome"))

                        if titulo_art:
                            artigos_para_salvar.append((
                                slug, nome_professor, prof.get("sigla"),
                                clean_value(ano_art), clean_value(titulo_art),
                                clean_value(journal), clean_value(doi),
                                clean_value(palavras.get("palavrasChaves"))
                            ))

# projetos de pesquisa (aparece em dadosGerais/atuacoesProfissionais)
                global _projetos_debug_logged
                dados_gerais = data.get("dadosGerais", {}) or {}
                atuacoes = dados_gerais.get("atuacoesProfissionais", {}).get("atuacaoProfissional", [])

                if not _projetos_debug_logged:
                    if not atuacoes:
                        log(f"[{sigla}] dadosGerais/atuacoesProfissionais ausente ou vazio")
                    else:
                        log(f"[{sigla}] encontrado dadosGerais/atuacoesProfissionais com {len(atuacoes)} entradas")
                    _projetos_debug_logged = True

                for atuacao in atuacoes:
                    for atividade in atuacao.get("atividadesDeParticipacaoEmProjeto", []):
                        for participacao in atividade.get("participacaoEmProjeto", []):
                            for proj in participacao.get("projetoDePesquisa", []):
                                titulo_proj = proj.get("nomeDoProjeto") or proj.get("nomeDoProjetoIngles")
                                descricao = proj.get("descricaoDoProjeto") or proj.get("descricaoDoProjetoIngles")
                                natureza = proj.get("natureza")

                                # Monta a equipe (lista de integrantes)
                                equipe = []
                                equipe_obj = proj.get("equipeDoProjeto") or {}
                                for integrante in (equipe_obj.get("integrantesDoProjeto") or []):
                                    if not isinstance(integrante, dict):
                                        continue
                                    nome = integrante.get("nomeParaCitacao") or integrante.get("nomeCompleto")
                                    if not nome:
                                        continue
                                    if str(integrante.get("flagResponsavel") or "").upper() in ("SIM", "S", "TRUE", "1"):
                                        nome = f"{nome} (Responsável)"
                                    equipe.append(nome)
                                equipe_str = "; ".join(equipe)

                                # Monta financiadores
                                financiadores = []
                                for f in (proj.get("financiadoresDoProjeto") or []):
                                    if isinstance(f, dict):
                                        nome = f.get("nomeFinanciador") or f.get("nome") or f.get("instituicao")
                                        if not nome:
                                            nome = "; ".join(str(v) for v in f.values() if v)
                                        if nome:
                                            financiadores.append(nome)
                                    else:
                                        financiadores.append(str(f))
                                financiadores_str = "; ".join(financiadores)

                                nome_professor = clean_value(prof.get("nome"))

                                if titulo_proj:
                                    projetos_para_salvar.append((
                                        slug, nome_professor, prof.get("sigla"),
                                        clean_value(titulo_proj), clean_value(descricao),
                                        clean_value(natureza), clean_value(equipe_str), clean_value(financiadores_str)
                                    ))

            if tccs_para_salvar:
                db_manager.save_tccs(tccs_para_salvar)
            if artigos_para_salvar:
                db_manager.save_artigos(artigos_para_salvar)
                art_count += len(artigos_para_salvar)
                log(f"[{sigla}] {len(artigos_para_salvar)} artigos salvos")
                if progress_callback_art:
                    progress_callback_art(art_count, "?")
            if projetos_para_salvar:
                db_manager.save_projetos(projetos_para_salvar)
                proj_count += len(projetos_para_salvar)
                log(f"[{sigla}] {len(projetos_para_salvar)} projetos salvos")
    
    log(f"[{sigla}] Todos os TCCs salvos.")
    if progress_callback_art:
        log(f"[{sigla}] Total de artigos coletados: {art_count}")
        log(f"[{sigla}] Total de projetos coletados: {proj_count}")

async def run_for_institution(sigla, base_url, uf, db_manager, callbacks):
    """Executa o pipeline completo para uma instituição."""
    log(f"=== {sigla}: Iniciando coleta ===")
    
    professores = await fetch_professores(sigla, base_url, db_manager, callbacks.get('prof_progress'))
    log(f"[{sigla}] Total de professores encontrados: {len(professores)}")
    
    await fetch_detalhes(sigla, base_url, uf, professores, db_manager, callbacks.get('det_progress'), callbacks.get('art_progress'))
    
    log(f"=== {sigla}: Coleta concluída ===")
