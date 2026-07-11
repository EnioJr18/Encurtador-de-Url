# EncurtarJR - Encurtador de URLs com Flask

![CI](https://github.com/EnioJr18/Encurtador-de-Url/actions/workflows/ci.yml/badge.svg)

O EncurtarJR nasceu como um dos meus primeiros projetos Flask: um encurtador de links direto ao ponto. Ao longo das refatorações, ele se tornou uma aplicação mais organizada para praticar arquitetura backend, segurança básica, migrations, testes e experiência de uso, sem perder a proposta original.

O foco deste repositório é mostrar essa evolução com decisões técnicas incrementais e uma aplicação web funcional, não se apresentar como uma solução enterprise ou um SaaS completo.

## Status

- Projeto em evolução e preparado para portfólio backend.
- Testes automatizados locais com Pytest.
- Demo publicada no Render: [encurtador-de-url-8ris.onrender.com](https://encurtador-de-url-8ris.onrender.com)

## Demonstração

![Tela do EncurtarJR](https://github.com/user-attachments/assets/44767606-6ed7-45f9-a1d7-43b39ee4d26d)

## Funcionalidades

- Encurtamento de URLs com validação no backend.
- Links personalizados com regras de formato e bloqueio de slugs reservados.
- Redirecionamento por código curto.
- Geração de QR Code para cada link.
- Cadastro, login e logout com senha armazenada em hash.
- Painel do usuário para visualizar os próprios links e seus acessos.
- Contador de cliques atualizado diretamente no banco.
- Limite freemium para criação anônima de links.
- Páginas amigáveis para erros `400`, `404`, `429` e `500`.
- Interface responsiva com Bootstrap, Jinja2 e componentes reutilizáveis.

## Diferenciais Técnicos

- Application factory para inicialização previsível da aplicação.
- Blueprints para separar rotas de autenticação, página principal e URLs.
- Camada de service para concentrar a regra de criação de links.
- Extensões Flask centralizadas em `extensions.py`.
- Flask-Migrate/Alembic no lugar de criação automática de tabelas ao iniciar.
- Configuração por ambiente para desenvolvimento, testes e produção.
- Geração segura de códigos curtos com `secrets` e tratamento de colisões.
- Proteção CSRF em formulários HTML e rate limit nas ações mais sensíveis.
- Logging básico e tratamento centralizado de erros.
- Testes de fluxos reais usando cliente Flask e SQLite em memória.

## Tecnologias

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
- PostgreSQL no ambiente de produção, hospedado no Neon

**Frontend**

- HTML5
- CSS3
- Bootstrap
- Jinja2
- Boxicons

**Qualidade e entrega**

- Pytest
- Alembic
- Git e GitHub
- Render

## Arquitetura

```text
.
├── app.py                 # ponto de entrada compatível com Flask CLI
├── config.py              # configurações por ambiente
├── encurtarjr/
│   ├── __init__.py        # application factory e registro de blueprints
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

As rotas ficam finas e delegam a criação de links ao service. A factory inicializa as extensões e registra os blueprints, enquanto as configurações de ambiente ficam fora da regra de negócio.

## Como Rodar Localmente

### Pré-requisitos

- Python 3.13 ou superior
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

### Linux/macOS

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

## Variáveis de Ambiente

O arquivo `.env.example` fica versionado como referência. O `.env` real é ignorado pelo Git e não deve conter segredos em commits.

Exemplo seguro para desenvolvimento:

```env
APP_ENV=development
SECRET_KEY=troque-essa-chave
DATABASE_URL=sqlite:///urls.db
FLASK_APP=app.py
FLASK_DEBUG=1
```

No desenvolvimento, o projeto usa SQLite local por padrão. Em produção, `SECRET_KEY` e `DATABASE_URL` são obrigatórias. URLs antigas iniciadas por `postgres://` também são normalizadas para `postgresql://` pela configuração.

Opcionalmente, `RATELIMIT_STORAGE_URI` pode ser configurada. Em desenvolvimento, o padrão é `memory://`.

## Banco de Dados e Migrations

As tabelas não são criadas automaticamente na inicialização. Para preparar um banco novo, use:

```bash
flask --app app.py db upgrade
```

Quando houver uma alteração real nos models no futuro:

```bash
flask --app app.py db migrate -m "descricao da alteracao"
flask --app app.py db upgrade
```

Evite executar migrations contra o banco remoto Neon durante testes ou refatorações locais sem intenção. Para bancos locais existentes antes da adoção do Alembic, `flask db stamp head` só deve ser usado depois de conferir que o schema atual corresponde à migration inicial.

## Testes

```bash
pytest
```

Atualmente, a suíte possui **26 testes**. Ela cobre, entre outros fluxos:

- página inicial;
- cadastro e login, incluindo credenciais inválidas;
- criação de URL válida;
- URLs sem `http://` ou `https://` e esquemas perigosos;
- códigos personalizados inválidos, reservados e duplicados;
- painel protegido e painel com links;
- redirecionamento e contador de cliques;
- respostas amigáveis para erros `400`, `404`, `429` e `500`;
- CSRF e rate limit em cenários controlados.

Nos testes, CSRF e rate limit são desativados pela configuração de teste para que os fluxos possam ser exercitados sem depender de sessão ou armazenamento externo. A proteção permanece ativa nos ambientes de desenvolvimento e produção.

## Segurança e Validações

- Senhas protegidas com hash via Flask-Bcrypt.
- `SECRET_KEY` fornecida por variável de ambiente em produção.
- CSRF aplicado aos formulários Flask-WTF.
- Rate limit em cadastro, login, criação de links e QR Code.
- Validação de URL apenas para `http://` e `https://`.
- Validação de códigos personalizados e bloqueio de palavras reservadas.
- Geração de short codes com `secrets` e tratamento de colisões no banco.
- Erros tratados com páginas amigáveis, sem apresentar stack trace ao usuário.

## Deploy

O deploy da aplicação é feito no Render. Em produção, o banco PostgreSQL é hospedado no Neon e as variáveis `SECRET_KEY` e `DATABASE_URL` precisam estar configuradas no ambiente correto.

Antes de publicar uma mudança de schema, aplique as migrations no banco de destino com cuidado e confirme a `DATABASE_URL` ativa.

## Aprendizados

Este projeto foi uma oportunidade de ir além de rotas e templates básicos do Flask. A evolução incremental trouxe prática real com organização de aplicação, separação de responsabilidades, migrations, validações, proteção de formulários, controle de requisições, testes e melhorias de interface.

Mais do que reescrever tudo de uma vez, a proposta foi entender os riscos do projeto inicial e melhorar cada parte preservando o que já funcionava.

## Roadmap

- [ ] CI com GitHub Actions e badge no README.
- [ ] Analytics mais detalhado por link.
- [ ] Expiração de links.
- [ ] Feedback de cópia de link ainda mais completo.
- [ ] API REST.
- [ ] Redis para rate limit em produção.
- [ ] Painel administrativo.
- [ ] Melhorias adicionais de acessibilidade.

## Autor

**Enio Jr**
Backend Developer em formação

- [LinkedIn](https://www.linkedin.com/in/enioeduardojr/)
- [GitHub](https://github.com/EnioJr18)
