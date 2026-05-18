import os  
import mysql.connector
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlparse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
app = FastAPI()

# Configuração do CORS (para o index.html conseguir acessar a API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Descobre o caminho da pasta principal do projeto (um nível acima da pasta back-end)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Monta os caminhos exatos para as pastas do front-end
PATH_HOME = os.path.join(BASE_DIR, "docs")
PATH_AGENDAS = os.path.join(BASE_DIR, "agendas_consultas_vestibulares_etc")

# Avisa ao FastAPI para disponibilizar as pastas usando os caminhos absolutos
app.mount("/docs", StaticFiles(directory=PATH_HOME), name="docs")
app.mount("/agendas_consultas_vestibulares_etc", StaticFiles(directory=PATH_AGENDAS), name="agendas")

# Rota para a página inicial
@app.get("/")
def read_index():
    return FileResponse(os.path.join(PATH_HOME, "helphub.html"))




def get_db_connection():
    try:
        url = os.environ.get("DATABASE_URL")
        if url:
            parsed = urlparse(url)
            return mysql.connector.connect(
                host=parsed.hostname,
                port=parsed.port or 3306,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path.lstrip("/")
            )
        else:
            # fallback para rodar local
            return mysql.connector.connect(
                host="localhost",
                port=3307,
                user="root",
                password="",
                database="helphub"
            )
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

# ─────────────────────────────────────────────
#  MODELOS
# ─────────────────────────────────────────────

class LoginSchema(BaseModel):
    email: str
    senha: str

class CadastroAlunoSchema(BaseModel):
    nome: str
    telefone: str
    email: str
    senha: str
    idade: int
    vestibulares: Optional[List[int]] = []
    responsavel_nome: Optional[str] = None
    responsavel_telefone: Optional[str] = None

class CadastroVoluntarioSchema(BaseModel):
    nome: str
    telefone: str
    email: str
    senha: str
    materias: Optional[List[str]] = []
    disponibilidade: Optional[List[str]] = []
    sobre: Optional[str] = None

class ConteudoSchema(BaseModel):
    title: str
    materia: str
    desc: str
    link: Optional[str] = "#"


# ─────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────

@app.post("/login")
def login(dados: LoginSchema):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, nome FROM usuarios WHERE email = %s AND senha_hash = %s",
            (dados.email, dados.senha)
        )
        usuario = cursor.fetchone()

        if not usuario:
            raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")

        # Descobre o tipo verificando qual tabela tem o registro
        cursor.execute("SELECT id FROM alunos WHERE usuario_id = %s", (usuario["id"],))
        tipo = "aluno" if cursor.fetchone() else "voluntario"

        return {
            "status": "success",
            "message": f"Bem-vindo, {usuario['nome']}!",
            "usuario": {
                "id": usuario["id"],
                "nome": usuario["nome"],
                "tipo": tipo
            }
        }
    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
#  CADASTRO ALUNO
# ─────────────────────────────────────────────

@app.post("/cadastrar/aluno")
def cadastrar_aluno(dados: CadastroAlunoSchema):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verifica se o e-mail ja existe
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (dados.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="E-mail ja cadastrado.")

        # Insere na tabela geral de usuarios
        cursor.execute(
            "INSERT INTO usuarios (nome, telefone, email, senha_hash) VALUES (%s, %s, %s, %s)",
            (dados.nome, dados.telefone, dados.email, dados.senha)
        )
        usuario_id = cursor.lastrowid

        # Insere na tabela especifica de alunos
        cursor.execute(
            "INSERT INTO alunos (usuario_id, idade, responsavel_nome, responsavel_telefone) VALUES (%s, %s, %s, %s)",
            (usuario_id, dados.idade, dados.responsavel_nome, dados.responsavel_telefone)
        )
        aluno_id = cursor.lastrowid

        # Vincula vestibulares de interesse
        for vest_id in dados.vestibulares:
            cursor.execute(
                "INSERT IGNORE INTO aluno_vestibulares (aluno_id, vestibular_id) VALUES (%s, %s)",
                (aluno_id, vest_id)
            )

        conn.commit()
        return {"status": "success", "message": "Aluno cadastrado com sucesso!"}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
#  CADASTRO VOLUNTARIO
# ─────────────────────────────────────────────

@app.post("/cadastrar/voluntario")
def cadastrar_voluntario(dados: CadastroVoluntarioSchema):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verifica se o e-mail ja existe
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (dados.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="E-mail ja cadastrado.")

        # Insere na tabela geral de usuarios
        cursor.execute(
            "INSERT INTO usuarios (nome, telefone, email, senha_hash) VALUES (%s, %s, %s, %s)",
            (dados.nome, dados.telefone, dados.email, dados.senha)
        )
        usuario_id = cursor.lastrowid

        # Insere na tabela de voluntarios
        cursor.execute(
            "INSERT INTO voluntarios (usuario_id, sobre_voce) VALUES (%s, %s)",
            (usuario_id, dados.sobre)
        )
        voluntario_id = cursor.lastrowid

        # Vincula matérias (busca id pelo nome)
        for materia_nome in dados.materias:
            cursor.execute("SELECT id FROM materias WHERE nome = %s", (materia_nome,))
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    "INSERT IGNORE INTO voluntario_materias (voluntario_id, materia_id) VALUES (%s, %s)",
                    (voluntario_id, row[0])
                )

        # Vincula disponibilidade (busca id pelo nome)
        for dia_nome in dados.disponibilidade:
            cursor.execute("SELECT id FROM dias_semana WHERE nome = %s", (dia_nome,))
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    "INSERT IGNORE INTO voluntario_disponibilidade (voluntario_id, dia_id) VALUES (%s, %s)",
                    (voluntario_id, row[0])
                )

        conn.commit()
        return {"status": "success", "message": "Voluntario cadastrado com sucesso!"}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
#  CONTEUDOS
# ─────────────────────────────────────────────

@app.get("/cards")
def get_cards():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            c.id, 
            c.titulo AS title, 
            m.nome AS materia_nome, 
            c.descricao AS `desc`, 
            c.link 
        FROM conteudos c
        JOIN materias m ON c.materia_id = m.id
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        materia_original = row['materia_nome'].lower()
        mapeamento = {
            "matemática": "matematica",
            "física": "fisica",
            "geografia": "geografia",
            "história": "historia",
            "filosofia": "filosofia",
            "redação": "redacao"
        }
        row['materia'] = mapeamento.get(materia_original, materia_original)

    cursor.close()
    conn.close()
    return rows


@app.post("/cards")
def add_card_db(card: ConteudoSchema):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM materias WHERE nome LIKE %s", (card.materia,))
        materia_res = cursor.fetchone()

        if not materia_res:
            raise HTTPException(status_code=400, detail="Materia nao encontrada no banco.")

        materia_id = materia_res[0]

        query = "INSERT INTO conteudos (titulo, materia_id, descricao, link) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (card.title, materia_id, card.desc, card.link))

        conn.commit()
        return {"status": "success", "message": "Conteudo salvo no banco de dados!"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
#  AGENDAS
# ─────────────────────────────────────────────

@app.get("/agendas")
def get_agendas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = "SELECT id, materia, titulo, data, horario, voluntario, vagas_atuais, vagas_totais FROM agendas"
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            if row['data']:
                row['data'] = row['data'].strftime('%Y-%m-%d')
            if row['horario']:
                total_seconds = int(row['horario'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                row['horario'] = f"{hours:02d}:{minutes:02d}"

        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@app.delete("/cards/{card_id}")
def delete_card(card_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM conteudos WHERE id = %s", (card_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Conteúdo não encontrado.")
        conn.commit()
        return {"status": "success", "message": "Conteúdo removido."}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()        


if __name__ == "__main__":
    import uvicorn
    import os
    
    # O Render injeta a porta correta aqui. Se for no seu PC, ele usa a 8000.
    port = int(os.environ.get("PORT", 8000))
    
    # O host "0.0.0.0" permite que o Render receba acessos de fora
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)