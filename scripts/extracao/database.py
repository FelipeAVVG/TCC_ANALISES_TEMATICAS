import sqlite3
import config

def clean_value(val):
    """Retorna None para valores considerados vazios, senão retorna o próprio valor."""
    if val in (None, "", "Não disponível"):
        return None
    return val


class DatabaseManager:
    """Gerencia todas as operações do banco de dados SQLite."""

    def __init__(self, db_name=config.DB_NAME):
        self.db_name = db_name

    def _get_connection(self):
        """Retorna uma conexão com o banco de dados."""
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _column_exists(self, cur, table_name, column_name):
        cur.execute(f"PRAGMA table_info({table_name})")
        cols = [row[1] for row in cur.fetchall()]
        return column_name in cols

    def init_db(self):
        """Cria as tabelas e índices necessários se não existirem.

        Observação:
        - Em bancos novos, as tabelas já nascem com professor_id e FOREIGN KEY.
        - Em bancos antigos, adicionamos a coluna professor_id via ALTER TABLE para
          evitar quebra, mas a constraint FK só existirá automaticamente em bancos
          criados do zero com este schema.
        """
        with self._get_connection() as conn:
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS professores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sigla TEXT,
                nome TEXT,
                campus TEXT,
                cargo TEXT,
                slug TEXT,
                url_final TEXT,
                UNIQUE(slug, sigla)
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS tccs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                professor_id INTEGER,
                slug_professor TEXT,
                nome_professor TEXT,
                sigla TEXT,
                instituicao TEXT,
                UF TEXT,
                campus TEXT,
                ano TEXT,
                curso TEXT,
                autores TEXT,
                titulo TEXT,
                resumo TEXT,
                palavras_chaves TEXT,
                UNIQUE(professor_id, titulo),
                FOREIGN KEY (professor_id) REFERENCES professores(id)
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS artigos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                professor_id INTEGER,
                slug_professor TEXT,
                nome_professor TEXT,
                sigla TEXT,
                ano TEXT,
                titulo TEXT,
                journal TEXT,
                doi TEXT,
                palavras_chaves TEXT,
                UNIQUE(professor_id, titulo),
                FOREIGN KEY (professor_id) REFERENCES professores(id)
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS projetos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                professor_id INTEGER,
                slug_professor TEXT,
                nome_professor TEXT,
                sigla TEXT,
                titulo TEXT,
                descricao TEXT,
                natureza TEXT,
                equipe TEXT,
                financiadores TEXT,
                UNIQUE(professor_id, titulo),
                FOREIGN KEY (professor_id) REFERENCES professores(id)
            )
            """)

            # Migração leve para bancos antigos já existentes
            if not self._column_exists(cur, "tccs", "professor_id"):
                cur.execute("ALTER TABLE tccs ADD COLUMN professor_id INTEGER")
            if not self._column_exists(cur, "artigos", "professor_id"):
                cur.execute("ALTER TABLE artigos ADD COLUMN professor_id INTEGER")
            if not self._column_exists(cur, "projetos", "professor_id"):
                cur.execute("ALTER TABLE projetos ADD COLUMN professor_id INTEGER")

            # índices para acelerar consultas e joins
            cur.execute("CREATE INDEX IF NOT EXISTS idx_professores_slug ON professores(slug)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_professores_sigla ON professores(sigla)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_professores_slug_sigla ON professores(slug, sigla)")

            cur.execute("CREATE INDEX IF NOT EXISTS idx_tccs_professor_id ON tccs(professor_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_tccs_slugprof ON tccs(slug_professor)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_tccs_sigla ON tccs(sigla)")

            cur.execute("CREATE INDEX IF NOT EXISTS idx_artigos_professor_id ON artigos(professor_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_artigos_slugprof ON artigos(slug_professor)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_artigos_sigla ON artigos(sigla)")

            cur.execute("CREATE INDEX IF NOT EXISTS idx_projetos_professor_id ON projetos(professor_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_projetos_slugprof ON projetos(slug_professor)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_projetos_sigla ON projetos(sigla)")

            conn.commit()

    def save_professores(self, sigla, professores):
        """Salva uma lista de professores no banco de dados."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            prof_data = [
                (sigla, p["nome"], p["campus"], p["cargo"], p["slug"], p["url_final"])
                for p in professores
            ]
            cur.executemany("""
            INSERT OR IGNORE INTO professores (sigla, nome, campus, cargo, slug, url_final)
            VALUES (?, ?, ?, ?, ?, ?)
            """, prof_data)
            conn.commit()

    def get_professor_id(self, sigla, slug):
        """Retorna o ID do professor a partir de sigla + slug."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id
                FROM professores
                WHERE sigla = ? AND slug = ?
                LIMIT 1
            """, (sigla, slug))
            row = cur.fetchone()
            return row[0] if row else None

    def save_tccs(self, tccs_data):
        """Salva uma lista de TCCs no banco de dados."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.executemany("""
            INSERT OR IGNORE INTO tccs (
                professor_id, slug_professor, nome_professor, sigla, instituicao, UF, campus, ano, curso,
                autores, titulo, resumo, palavras_chaves
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tccs_data)
            conn.commit()

    def save_artigos(self, artigos_data):
        """Salva uma lista de artigos científicos no banco de dados."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.executemany("""
            INSERT OR IGNORE INTO artigos (
                professor_id, slug_professor, nome_professor, sigla, ano, titulo,
                journal, doi, palavras_chaves
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, artigos_data)
            conn.commit()

    def save_projetos(self, projetos_data):
        """Salva uma lista de projetos no banco de dados."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.executemany("""
            INSERT OR IGNORE INTO projetos (
                professor_id, slug_professor, nome_professor, sigla, titulo,
                descricao, natureza, equipe, financiadores
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, projetos_data)
            conn.commit()

    def get_status_summary(self):
        """Busca um resumo de professores e TCCs por instituição."""
        with self._get_connection() as conn:
            cur = conn.cursor()

            cur.execute("SELECT sigla, COUNT(DISTINCT slug) FROM professores GROUP BY sigla")
            prof_map = dict(cur.fetchall())

            cur.execute("SELECT sigla, COUNT(*) FROM tccs GROUP BY sigla")
            tcc_map = dict(cur.fetchall())

            cur.execute("SELECT sigla, COUNT(*) FROM artigos GROUP BY sigla")
            art_map = dict(cur.fetchall())

            cur.execute("SELECT sigla, COUNT(*) FROM projetos GROUP BY sigla")
            proj_map = dict(cur.fetchall())

            total_professores = 0
            total_tccs = 0
            total_artigos = 0
            total_projetos = 0

            totalizador_uf = {}

            for sigla, total_prof in prof_map.items():
                total_tcc = tcc_map.get(sigla, 0)
                total_art = art_map.get(sigla, 0)
                total_proj = proj_map.get(sigla, 0)
                totalizador_uf[sigla] = {
                    "professores": total_prof,
                    "tccs": total_tcc,
                    "artigos": total_art,
                    "projetos": total_proj
                }
                total_professores += total_prof
                total_tccs += total_tcc
                total_artigos += total_art
                total_projetos += total_proj

            return {
                "totalizador_uf": totalizador_uf,
                "total_professores": total_professores,
                "total_tccs": total_tccs,
                "total_artigos": total_artigos,
                "total_projetos": total_projetos
            }
