# RocketLab 2026.2 — repositório base

> O produto final construído em cima desta base se chama **Moovie** (ver seção
> "Identidade visual: Moovie" mais abaixo) — o nome `RocketLab` abaixo é só o
> nome de referência do repositório-base fornecido na atividade.

Base inicial para evoluir a atividade do RocketLab 2026.2. Ela preserva a organização do backend,
o modelo relacional do catálogo de filmes em SQLAlchemy 2.0 e o histórico de
migrações com Alembic, sem incluir interface, dados CSV, endpoints de negócio
ou rotinas de carga.

> **Nota:** `RocketLab` é apenas o nome de referência desta base. O diretório,
> nome do pacote, título da API e arquivo do banco podem ser renomeados para o
> que preferirem; eles não representam uma exigência da
> estrutura-base.

## Estrutura

```text
.
├── backend/
│   ├── app/
│   │   ├── api/v1/        # ponto de composição dos futuros routers
│   │   ├── core/          # configurações e logging
│   │   ├── db/            # Base ORM, engine e sessões
│   │   └── movies/        # modelos SQLAlchemy do domínio de filmes
│   ├── migrations/        # ambiente e revisões Alembic
│   └── tests/
└── README.md
```

## Execução

Requer Python 3.11 ou superior.

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp .env.example .env
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
```

A API mínima ficará disponível em `http://localhost:8000`; use
`http://localhost:8000/docs` para a documentação automática. O endpoint
`GET /health` permite conferir se a aplicação iniciou corretamente.

## Banco de dados e migrações

O modelo usa um esquema estrela para o catálogo de filmes:

- dimensões de filmes, gêneros, pessoas, produtoras e resumo de avaliações;
- fato de desempenho financeiro e de engajamento;
- tabelas de associação N:N entre filmes, gêneros, produtoras e pessoas;

O schema corresponde aos nove arquivos CSV atuais da camada Diamond, com a
adição de `movie_reviews`: uma avaliação individual por linha, na escala 0–10.
A tabela aceita diretamente as colunas `sk_movie_review_id`, `sk_movie_id`,
`nome`, `nota` e `comentario` do CSV enviado separadamente. `created_at` é
gerado pelo banco. O contexto generativo não faz parte desta base.

O repositório não inclui CSVs nem rotinas de carga. Para usar avaliações,
importe primeiro os filmes em `dim_movies` e depois o CSV de `movie_reviews`.

As tabelas são criadas exclusivamente pelo Alembic. Para evoluir os modelos,
crie uma revisão e aplique-a:

```bash
cd backend
.venv/bin/alembic revision --autogenerate -m "descreva a alteração"
.venv/bin/alembic upgrade head
```

O banco padrão é SQLite local em `backend/rocketlab.db`. Ajuste
`DATABASE_URL` no arquivo `.env` para usar outro banco compatível.

---

## Sistema de Avaliação de Filmes — módulo completo

A partir da base acima, foi implementado o módulo completo de cadastro,
catálogo, busca, avaliações e média de notas, além do frontend em
Vite + React + TypeScript.

### Como rodar tudo, do zero

```bash
# 1) Backend
cd backend
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp .env.example .env
.venv/bin/alembic upgrade head

# 1.5) Crie a conta do Administrador (necessária para cadastrar/editar/remover filmes)
.venv/bin/python -m scripts.seed_admin

# 2) Popular o banco com os CSVs oficiais da atividade
#    Coloque os 9 arquivos .csv (dos dois zips entregues) em backend/seed_data/,
#    usando os nomes originais (dim_movies.csv, movies_reviews.csv, etc. —
#    ver scripts/seed.py para a lista completa) e rode:
.venv/bin/python -m scripts.seed
#    Carga completa (~1,7 milhão de linhas somadas) leva menos de 1 minuto.

# 3) Suba a API
.venv/bin/uvicorn app.main:app --reload
# -> http://localhost:8000/docs

# 4) Frontend (em outro terminal)
cd frontend
npm install
cp .env.example .env
npm run dev
# -> http://localhost:5173
```

### Endpoints da API (`/api/v1`)

| Método | Rota                          | Descrição                                             |
|--------|-------------------------------|--------------------------------------------------------|
| GET    | `/movies`                     | Catálogo paginado (`page`, `size`, `q`, `genero`)       |
| GET    | `/movies/{sk_movie_id}`       | Detalhes de um filme + lista de avaliações              |
| POST   | `/movies`                     | Cadastra um filme                                       |
| PUT    | `/movies/{sk_movie_id}`       | Atualiza um filme                                       |
| DELETE | `/movies/{sk_movie_id}`       | Remove um filme (avaliações são removidas em cascata)   |
| POST   | `/movies/{sk_movie_id}/reviews` | Adiciona uma avaliação (nota 0–10 + comentário)       |
| GET    | `/genres`                     | Lista os gêneros já cadastrados (para o filtro da UI)   |

Documentação interativa (Swagger) em `http://localhost:8000/docs`.

### Sobre os CSVs oficiais da atividade

O `scripts/seed.py` foi ajustado e testado (carga completa das ~1,7 milhão
de linhas, com checagem de integridade referencial via
`PRAGMA foreign_key_check`) com os 9 CSVs oficiais fornecidos na atividade:
`dim_companies`, `dim_genres`, `dim_movies`, `dim_people`, `dim_reviews`,
`bridge_movie_company`, `bridge_movie_genre`, `bridge_movie_person`,
`fact_movies_performance` e `movies_reviews`. As colunas já batem 1:1 com
`app/movies/models.py`, sem necessidade de ajuste manual.

Um detalhe da base que o `seed.py` já corrige automaticamente: cerca de
2.000 campos de texto (títulos e sinopses) vieram da fonte original com uma
camada extra de aspas envolvendo o campo inteiro (ex: o texto chega como
`"biography: ""stone cold"" steve austin's last match"` quando o valor de
verdade é `biography: "stone cold" steve austin's last match`). O seed
desfaz esse escape extra (em até duas camadas, quando necessário) para
qualquer coluna de texto, preservando apelidos entre aspas que fazem parte
do título de verdade (ex: `Satie's "Parade"`). Isso é aplicado direto na
carga; não precisa editar os CSVs.

Também existem alguns títulos duplicados com `sk_movie_id`/`id_filme`
diferentes — trate como entradas distintas normalmente (é a base real,
não é um bug).

### Escala de notas: 0 a 10

Conforme confirmado pelo professor, as avaliações usam nota de 0 a 10
(não estrelas de 1 a 5), o que já bate certinho com a `CheckConstraint`
(`nota BETWEEN 0 AND 10`) definida em `MovieReview` — API e frontend
trabalham diretamente nessa escala, sem nenhuma conversão.

### Média de avaliações

A tabela `dim_reviews` (resumo por filme) é atualizada a cada nova
avaliação (`qtd_avaliacoes_usuarios` e `nota_media_usuarios`), em vez de
recalculada com uma query de agregação a cada leitura — mais alinhado ao
propósito de resumo do esquema estrela fornecido.

### Estrutura adicionada

```text
backend/
├── app/auth/
│   ├── models.py         # tabela admin_users
│   ├── repository.py      # acesso a dados do admin
│   ├── service.py          # autenticação (login)
│   ├── dependencies.py      # get_current_admin (protege rotas)
│   └── router.py             # /auth/login, /logout, /me
├── app/movies/
│   ├── schemas.py         # Pydantic: entrada/saída da API
│   ├── repository.py       # só acesso a dados (SQLAlchemy)
│   ├── service.py           # regra de negócio (usa o repository)
│   └── router.py             # rotas de /movies e /genres
├── app/core/security.py   # hash de senha e token de sessão (stdlib)
├── scripts/seed.py         # carga inicial a partir dos CSVs da atividade
├── scripts/seed_admin.py    # cria a conta do Administrador
└── seed_data/                # coloque aqui os CSVs (não versionados)

frontend/
├── src/
│   ├── api/client.ts             # cliente HTTP (axios, com cookies)
│   ├── auth/AuthContext.tsx        # estado de login em toda a aplicação
│   ├── auth/ProtectedRoute.tsx      # redireciona para /login se necessário
│   ├── types/movie.ts             # tipos espelhando os schemas da API
│   ├── components/                # RatingControl, MovieCard, ReviewForm...
│   └── pages/                     # Catálogo, Login, Detalhes, Cadastro/Edição

.github/workflows/ci.yml   # roda testes e build a cada push/PR
```

### Identidade visual: Moovie

O frontend usa o nome **Moovie** (Moo + movie) com uma vaquinha de óculos 3D
como logo (`frontend/src/components/CowLogo.tsx`, SVG, sem dependência de
imagem externa), paleta escura roxo/verde neon (estilo luz negra/grafite) e
tipografia condensada (Bebas Neue) para títulos. Cards sem pôster usam um
gradiente roxo com o título em verde neon, em vez de aparentar "imagem
quebrada".

### ⚠️ Versionamento no Git

O `.git` original **não está incluído** neste pacote (foi removido de
propósito para não carregar o histórico/remoto do repositório-base). Antes
de entregar a atividade, confirme que a pasta está de fato versionada e
publicada no seu GitHub:

```bash
git status        # se der "not a git repository", rode o próximo bloco
```

Se não houver um `.git`:

```bash
git init
git remote add origin <link-do-seu-repositorio-no-github>
git add .
git commit -m "Módulo completo: catálogo, avaliações, seed e frontend"
git branch -M main
git push -u origin main
```

Se a pasta já era um clone git (e você só substituiu arquivos por cima,
sem apagar `.git`), basta `git add .`, `git commit` e `git push` normalmente.

### O que já está implementado (todos os requisitos da atividade)

- Cadastro de filmes (título, diretor, ano, gênero(s), sinopse)
- Catálogo paginado
- Detalhes do filme com histórico completo de avaliações
- Busca por título
- Atualização e remoção individual de filmes
- Avaliações (nota 0–10 + comentário)
- Média geral de avaliações por filme
- README com passo a passo de execução

### Itens de bônus ("criatividade") já feitos

- **Autenticação do Administrador** — login por cookie httpOnly; cadastrar,
  editar e remover filme exigem estar logado. Catálogo, detalhes e adicionar
  avaliação continuam públicos (qualquer visitante pode avaliar, só quem
  gerencia o catálogo precisa de login). Hash de senha com PBKDF2-HMAC-SHA256
  e token de sessão assinado (HMAC) — tudo com a biblioteca padrão do Python,
  sem dependências novas.
- **Arquitetura em camadas** no backend: `router → service → repository →
  SQLAlchemy`. `app/movies/repository.py` só acessa o banco;
  `app/movies/service.py` decide a regra de negócio (get-or-create de
  gênero/diretor, geração de id, resumo de avaliações).
- **CI** (`.github/workflows/ci.yml`): roda `ruff` + `pytest` no backend e
  `build` + testes no frontend a cada push/PR para `main`.
- Testes automatizados (`backend/tests/test_movies_api.py`,
  `backend/tests/test_auth.py` — login, senha errada, rotas protegidas sem
  sessão, logout)
- Filtros (busca por título + filtro por gênero)
- Responsividade (breakpoints em `styles.css`)
- Busca/filtro/página persistidos na URL (funciona com o botão Voltar do navegador)

### Itens de bônus ainda em aberto (ideias, se quiser ir além)

- Cache da listagem paginada
- Storybook para os componentes React
- Testes automatizados do frontend (ex: Vitest + Testing Library)
- Dashboard com estatísticas (gêneros mais comuns, notas médias por década...)
- Exportação do catálogo em CSV/JSON
- Loading skeletons e paginação "infinita" no catálogo
