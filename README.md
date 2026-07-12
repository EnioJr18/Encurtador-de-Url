# 🔗 EncurtarJR - Encurtador de URLs com Flask

![CI](https://github.com/EnioJr18/Encurtador-de-Url/actions/workflows/ci.yml/badge.svg?branch=main)
![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=flat-square&logo=bootstrap&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-45%20tests-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## 📌 Sobre o Projeto

O **EncurtarJR** nasceu como um dos meus primeiros projetos Flask: um encurtador de links simples, com autenticação e painel do usuário. Depois de várias sprints de refatoração, ele evoluiu para uma aplicação mais organizada e madura para portfólio backend, mantendo a ideia original.

O objetivo do repositório é demonstrar evolução técnica incremental: arquitetura Flask mais limpa, validações no backend, segurança básica, migrations, testes automatizados, CI, tratamento de erros e uma interface web responsiva. Ele não tenta se vender como um SaaS completo ou uma solução enterprise.

Demo: [encurtador-de-url-8ris.onrender.com](https://encurtador-de-url-8ris.onrender.com)

## ✅ Funcionalidades

- Encurtamento de URLs com validação no backend.
- Links personalizados com regras de formato e bloqueio de slugs reservados.
- Redirecionamento por código curto.
- Geração de QR Code em modal.
- Feedback visual ao copiar link curto.
- Cadastro, login e logout com senha armazenada em hash.
- Painel do usuário com:
  - resumo visual de links e cliques;
  - busca por URL original ou código curto;
  - filtro por links com ou sem acessos;
  - ordenação por recentes, antigos, acessos e código curto;
  - paginação.
- Painel administrativo protegido por `is_admin` com:
  - dashboard geral;
  - CRUD de usuários;
  - CRUD de links;
  - filtros e paginação;
  - comando CLI para promover administradores.
- Contador de cliques atualizado diretamente no banco.
- Limite freemium para criação anônima de links.
- Páginas amigáveis para erros `400`, `403`, `404`, `429` e `500`.
- Interface responsiva com Bootstrap, Jinja2 e componentes reutilizáveis.

## 🧠 Diferenciais Técnicos

- Application factory com `create_app()`.
- Blueprints para separar autenticação, página principal, URLs e admin.
- Camada de service para concentrar a regra de criação de links.
- Extensões Flask centralizadas em `extensions.py`.
- Flask-Migrate/Alembic para evolução do banco.
- Configuração por ambiente para desenvolvimento, testes e produção.
- Suporte a SQLite local e PostgreSQL em produção.
- Normalização de `postgres://` para `postgresql://`.
- `SECRET_KEY` exigida por variável de ambiente em produção.
- Proteção CSRF em formulários HTML.
- Rate limit em rotas sensíveis.
- Logging básico e handlers centralizados de erro.
- Testes de fluxos reais com Pytest e SQLite em memória.
- CI com GitHub Actions em cada push e pull request para `main`.

## 🛠️ Tecnologias

**Backend**

- Python
- Flask
- Flask-SQLAlchemy / SQLAlchemy
- Flask-Login
- Flask-Bcrypt
- Flask-Migrate
- Flask-WTF
- Flask-Limiter

**Banco de dados**

- SQLite no desenvolvimento local
- PostgreSQL em produção, hospedado no Neon

**Frontend**

- HTML5
- CSS3
- Bootstrap
- Jinja2
- Boxicons

**Qualidade e entrega**

- Pytest
- Alembic
- GitHub Actions
- Render

## 🧱 Arquitetura

```text
.
├── app.py                 # ponto de entrada compatível com Flask CLI
├── config.py              # configurações por ambiente
├── encurtarjr/
│   ├── __init__.py        # application factory e registro de blueprints
│   ├── commands.py        # comandos CLI administrativos
│   ├── decorators.py      # proteções como admin_required
│   ├── errors.py          # logging e handlers de erro
│   ├── extensions.py      # db, bcrypt, login, migrate, csrf e limiter
│   ├── forms.py           # formulários Flask-WTF
│   ├── models.py          # modelos SQLAlchemy
│   ├── utils.py           # validações e geração de short codes
│   ├── routes/            # blueprints de rotas
│   └── services/          # regras de negócio do encurtador
├── migrations/            # histórico Alembic versionado
├── static/                # CSS e assets
├── templates/             # páginas, partials e telas de erro
├── tests/                 # testes Pytest
└── requirements.txt
```

As rotas ficam mais finas e delegam regras importantes ao service. A factory inicializa as extensões e registra os blueprints, enquanto as configurações por ambiente ficam fora da regra de negócio.

## 🚀 Como Rodar Localmente

### Pré-requisitos

- Python 3.12 ou superior
- Git

### Windows (PowerShell)

```powershell
git clone https://github.com/EnioJr18/Encurtador-de-Url.git
cd Encurtador-de-Url

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
Copy-Item .env.example .env

flask --app app.py db upgrade
flask --app app.py run
```

Depois, acesse `http://127.0.0.1:5000`.

### 🐧Linux/🍎macOS

```bash
git clone https://github.com/EnioJr18/Encurtador-de-Url.git
cd Encurtador-de-Url

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

flask --app app.py db upgrade
flask --app app.py run
```

## 🔧 Variáveis de Ambiente

O arquivo `.env.example` fica versionado como referência. O `.env` real é ignorado pelo Git e não deve conter segredos em commits.

Exemplo para desenvolvimento:

```env
APP_ENV=development
SECRET_KEY=troque-essa-chave
DATABASE_URL=sqlite:///urls.db
FLASK_APP=app.py
FLASK_DEBUG=1
```

No desenvolvimento, o projeto usa SQLite local por padrão. Em produção, `SECRET_KEY` e `DATABASE_URL` são obrigatórias. O projeto também aceita URLs antigas iniciadas por `postgres://`, convertendo para `postgresql://`.

Opcionalmente, `RATELIMIT_STORAGE_URI` pode ser configurada. Em desenvolvimento, o padrão é `memory://`.

## 🗄️ Banco de Dados e Migrations

As tabelas não são criadas automaticamente ao iniciar a aplicação. Para preparar um banco novo, use:

```bash
flask --app app.py db upgrade
```

Quando houver uma alteração real nos models:

```bash
flask --app app.py db migrate -m "descricao da alteracao"
flask --app app.py db upgrade
```

Evite executar migrations contra o banco remoto Neon durante testes ou refatorações locais sem intenção. Confira sempre a `DATABASE_URL` ativa antes de aplicar migrations em produção.

## 🔐 Administradores

O acesso ao painel administrativo depende do campo `is_admin` do usuário.

Para promover um usuário existente:

```bash
flask --app app.py admin promote nome-do-usuario
```

Depois de promovido, o usuário verá o link **Admin** na navbar ao fazer login.

## 🧪 Testes Automatizados

```bash
pytest
```

Atualmente, a suíte possui **45 testes**. Ela cobre, entre outros fluxos:

- página inicial;
- cadastro e login, incluindo credenciais inválidas;
- mensagem traduzida do Flask-Login ao acessar rota protegida;
- criação de URL válida;
- URLs sem `http://` ou `https://` e esquemas perigosos;
- códigos personalizados inválidos, reservados e duplicados;
- painel do usuário protegido;
- busca, filtros, ordenação e paginação em `/urls`;
- QR Code em modal e feedback de cópia;
- redirecionamento e contador de cliques;
- painel administrativo protegido por `is_admin`;
- CRUD administrativo de usuários e links;
- filtros e paginação no admin;
- respostas amigáveis para erros `400`, `403`, `404`, `429` e `500`;
- CSRF e rate limit em cenários controlados.

Nos testes, CSRF e rate limit são desativados pela configuração de teste para que os fluxos possam ser exercitados sem depender de sessão real ou armazenamento externo. A proteção permanece ativa nos ambientes de desenvolvimento e produção.

## ⚙️ CI com GitHub Actions

O workflow `.github/workflows/ci.yml` roda em:

- `push` para `main`;
- `pull_request` para `main`;
- execução manual por `workflow_dispatch`.

A CI usa `APP_ENV=testing`, SQLite em memória e não depende de Neon, PostgreSQL externo, Docker ou deploy. Ela executa:

```bash
python -m compileall app.py config.py encurtarjr tests migrations
pytest
flask --app app.py routes
```

## 🛡️ Segurança e Validações

- Senhas protegidas com hash via Flask-Bcrypt.
- `SECRET_KEY` fornecida por variável de ambiente em produção.
- CSRF aplicado aos formulários HTML.
- Rate limit em cadastro, login, criação de links e QR Code.
- Validação de URL apenas para `http://` e `https://`.
- Bloqueio de esquemas perigosos como `javascript:`, `data:`, `file:` e similares.
- Validação de códigos personalizados e bloqueio de palavras reservadas.
- Geração de short codes com `secrets` e tratamento de colisões no banco.
- Erros tratados com páginas amigáveis, sem stack trace para o usuário.
- Admin protegido por `is_admin` e decorator dedicado.

## 🌐 Deploy

O deploy da aplicação é feito no Render. Em produção, o banco PostgreSQL é hospedado no Neon e as variáveis `SECRET_KEY` e `DATABASE_URL` precisam estar configuradas no ambiente correto.

Antes de publicar uma mudança de schema, aplique as migrations no banco de destino com cuidado e confirme a `DATABASE_URL` ativa.

## 📚 Aprendizados

Este projeto foi uma oportunidade de ir além de rotas e templates básicos do Flask. A evolução incremental trouxe prática real com organização de aplicação, separação de responsabilidades, migrations, validações, proteção de formulários, controle de requisições, testes, CI e melhorias de interface.

Mais do que reescrever tudo de uma vez, a proposta foi entender os riscos do projeto inicial e melhorar cada parte preservando o que já funcionava.

## 🗺️ Roadmap

- [ ] Histórico temporal de cliques.
- [ ] Analytics mais detalhado por link.
- [ ] Expiração de links.
- [ ] API REST.
- [ ] Redis para rate limit em produção.
- [ ] Exportação CSV.
- [ ] Melhorias contínuas de acessibilidade.

## 📄 Licença

Este projeto está sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas. Issues e pull requests são úteis principalmente quando focados em arquitetura, segurança, testes, documentação ou melhorias incrementais de regra de negócio.

## 👨‍💻 Autor

Desenvolvido por **Enio Jr.** para estudo, evolução técnica e portfólio backend/Engenharia de Software.

**Contato:**

- LinkedIn: https://www.linkedin.com/in/enioeduardojr
- Portfólio: https://eniojr18.github.io
- Email: eniojr100@gmail.com
- Instagram: https://www.instagram.com/eniojuniorrr
