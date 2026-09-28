# 🐄 Moovie

Catálogo e avaliação de filmes, inspirado no Letterboxd. Navegue por milhares de filmes, busque por título ou gênero, leia e escreva avaliações. O Administrador gerencia o catálogo.

<br>

## ✨ Funcionalidades

**Para qualquer visitante**
- Catálogo paginado com busca por título e filtro por gênero
- Página do filme com diretor, gêneros, sinopse, nota média e histórico de avaliações
- Adicionar uma avaliação (nota de 0 a 10 + resenha)

**Para o Administrador** (login necessário)
- Cadastrar, editar e remover filmes
- Dashboard com estatísticas do catálogo

<br>

## 🧰 Tecnologias

| Camada | Tecnologia |
|---|---|
| Frontend | React + TypeScript + Vite |
| Backend | FastAPI (Python 3.11+) |
| Banco de dados | SQLite · SQLAlchemy 2.0 · Alembic |
| Testes | Pytest · Vitest + Testing Library |
| CI | GitHub Actions |

<br>

## 🚀 Como rodar

**Pré-requisitos:** Python 3.11+ e Node 18+.

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate     # Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

alembic upgrade head              # cria as tabelas
python -m scripts.seed            # carrega os filmes (cerca de 1 minuto)
python -m scripts.seed_admin      # cria o login do Administrador

uvicorn app.main:app --reload
```

- Os CSVs já estão em `backend/seed_data/`, não precisa copiar nada.
- No `seed_admin`, o Git Bash não mostra a senha enquanto você digita. Digite normalmente e aperte Enter.

### 2. Frontend

Em outro terminal:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### 3. Acessar

| O quê | Endereço |
|---|---|
| Site | http://localhost:5173 |
| Documentação da API (Swagger) | http://localhost:8000/docs |

Para entrar como Administrador, clique em **Entrar** e use o e-mail e a senha criados no `seed_admin`.

> **Dia a dia:** depois da primeira vez, basta ativar o venv e rodar `uvicorn app.main:app --reload` no backend e `npm run dev` no frontend.

<br>

## 🧪 Testes

```bash
cd backend && pytest        # API, autenticação, dashboard e cache
cd frontend && npm test     # componentes React
```

Os dois rodam também automaticamente no GitHub Actions a cada push.

<br>

## 🔌 API

Base: `/api/v1` · 🔒 = exige login do Administrador

| Método | Rota | Descrição |
|---|---|---|
| GET | `/movies` | Catálogo paginado (`page`, `size`, `q`, `genero`) |
| GET | `/movies/{id}` | Detalhes do filme e suas avaliações |
| POST | `/movies` 🔒 | Cadastra um filme |
| PUT | `/movies/{id}` 🔒 | Atualiza um filme |
| DELETE | `/movies/{id}` 🔒 | Remove um filme |
| POST | `/movies/{id}/reviews` | Adiciona uma avaliação |
| GET | `/genres` | Lista os gêneros |
| GET | `/dashboard` 🔒 | Estatísticas do catálogo |
| POST | `/auth/login` · `/auth/logout` | Inicia e encerra a sessão |
| GET | `/auth/me` 🔒 | Administrador logado |

<br>

## 🗂️ Estrutura

```text
├── backend/
│   ├── app/
│   │   ├── auth/         login e sessão do Administrador
│   │   ├── movies/       catálogo (router → service → repository)
│   │   ├── stats/        dashboard
│   │   ├── core/         configuração, segurança e cache
│   │   └── db/           base ORM e sessão
│   ├── migrations/       Alembic
│   ├── scripts/          seed.py · seed_admin.py
│   ├── seed_data/        CSVs dos filmes
│   └── tests/
├── frontend/
│   └── src/              api · auth · components · pages · types
└── .github/workflows/    CI
```

<br>

## 💡 Decisões técnicas

- **Nota de 0 a 10**, a mesma escala do banco (`movie_reviews.nota`).
- **Média de avaliações** mantida em `dim_reviews` e atualizada a cada nova avaliação, sem recalcular tudo a cada leitura.
- **Arquitetura em camadas** no backend: `router → service → repository`, separando rotas, regras de negócio e acesso ao banco.
- **Autenticação** com cookie `httpOnly` e senha com hash PBKDF2, usando apenas a biblioteca padrão do Python.
- **Cache** em memória com validade de 60 s para o catálogo, os gêneros e o dashboard. Qualquer alteração (cadastro, edição, remoção ou nova avaliação) limpa o cache. Configurável em `CACHE_TTL_SECONDS` (`0` desliga).
- **Limpeza de dados no seed:** alguns títulos e sinopses da base vinham com aspas duplicadas em volta do texto inteiro, e o script remove esse excesso ao carregar. Nomes de produtoras que ficavam iguais depois da limpeza recebem um sufixo `(2)` para não perder nenhuma linha.
