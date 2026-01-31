# 🔗 Encurtador de URLs com Flask

![Status](https://img.shields.io/badge/Status-Concluído-success)
![Python](https://img.shields.io/badge/Python-3.13%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791)
![Deploy](https://img.shields.io/badge/Deploy-Render-black)

Um serviço completo de encurtamento de URLs, desenvolvido com **Python** e **Flask**, utilizando banco de dados **PostgreSQL** hospedado na nuvem. O projeto inclui um encurtador de URLs moderno, seguro e multi-usuário com sistema Freemium, geração de QR Codes e análise de cliques.

## 🚀 Demo Online

O projeto está rodando em produção! Acesse aqui:
👉 **https://encurtador-de-url-8ris.onrender.com**

---

## 📸 Demonstração Visual

![Image](https://github.com/user-attachments/assets/d47dc998-a11e-4ade-be49-81f88692b42b)

---

## 🚀 Sobre o Projeto

O **EncurtarJR** é uma aplicação web completa desenvolvida para transformar URLs longas e complexas em links curtos e amigáveis. 

Diferente de encurtadores simples, este projeto evoluiu para uma plataforma **SaaS (Software as a Service)**, implementando autenticação segura, gestão de links por usuário e um modelo de negócios "Freemium" que limita o uso anônimo para incentivar o cadastro.

### ✨ Funcionalidades Principais

* **✂️ Encurtamento Rápido:** Gere links curtos instantaneamente.
* **🎨 Links Personalizados:** O usuário pode escolher o sufixo (ex: `meusite.com/promocao`).
* **📱 QR Code Automático:** Todo link gera um QR Code para compartilhamento fácil.
* **📊 Estatísticas de Acesso:** Contador de cliques para monitorar o engajamento.
* **🔐 Sistema de Login Completo:** Cadastro, Login e Logout seguros com criptografia de senha.
* **👤 Painel do Usuário:** Área logada onde cada usuário gerencia apenas os seus próprios links.
* **💎 Modelo Freemium:** Usuários anônimos têm limite de links (Cookies/Session); cadastro desbloqueia recursos.
* **🛡️ Segurança:** Proteção contra acesso indevido e validação de dados.

---

## 🛠️ Tecnologias Utilizadas

O projeto foi construído utilizando as melhores práticas do ecossistema Python/Web:

* **Backend:** [Python](https://www.python.org/) + [Flask](https://flask.palletsprojects.com/)
* **Banco de Dados:** * *Desenvolvimento:* SQLite (Simples e rápido)
    * *Produção:* PostgreSQL (Hospedado no Neon Tech)
* **ORM:** SQLAlchemy (Gerenciamento eficiente do banco)
* **Autenticação:** Flask-Login + Flask-Bcrypt (Gestão de sessão e Hash de senhas)
* **Frontend:** HTML5, CSS3 Moderno (Responsivo), Jinja2 Templates.
* **Deploy:** Render (Aplicação) + Neon (Banco de Dados).

---

## 🗂️ Estrutura do Projeto

```bash
EncurtarJR/ 
├── static/             # Arquivos CSS, Imagens e Assets │ 
    ├── style.css       # Estilização principal 
    ├── style2.css      # Estilização secundária 
    └── assets/         # Logos e ícones 
├── templates/          # Arquivos HTML (Jinja2) │ 
    ├── index.html      # Página inicial │ 
    ├── login.html      # Tela de login │ 
    ├── register.html   # Tela de cadastro │ 
    └── urls.html       # Painel de links do usuário 
├── app.py              # Ponto de entrada da aplicação e configs 
├── controllers.py      # Lógica das rotas (Backend) 
├── models.py           # Estrutura do Banco de Dados (Tabelas) 
└── requirements.txt    # Lista de bibliotecas
```

## 🚀 Como Rodar o Projeto Localmente

Siga os passos abaixo para executar o projeto em sua máquina.

**Pré-requisitos:**
* **Python 3.13+**
* **Git**

**Passos:**
1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/EnioJr18/Encurtador-de-Url.git](https://github.com/EnioJr18/Encurtador-de-Url.git)
    cd Encurtador-de-Url
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Para macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure o Banco de Dados:**
    ```bash
    O projeto está configurado para criar o banco SQLite automaticamente na primeira execução.
    *Certifique-se de deletar qualquer arquivo `.db` antigo se houver mudanças na estrutura.*
    ```

5. **Configure as variáveis de ambiente**
Crie um arquivo ```.env (opcional)``` ou exporte as variáveis no terminal. Se não configurar, o projeto usará o SQLite localmente por padrão.


6.  **Execute a aplicação:**
    ```bash
    flask run
    ```

7.  Abra seu navegador e acesse `http://127.0.0.1:5000`.

## 📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🤝 Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.
1.  Faça um Fork do projeto
2.  Crie uma Branch para sua Feature (`git checkout -b feature/Incrível`)
3.  Faça o Commit (`git commit -m 'Add some Incrível'`)
4.  Push para a Branch (`git push origin feature/Incrível`)
5.  Abra um Pull Request

---

## 👨‍💻 Autor
Desenvolvido por Enio Jr como parte de um portfólio de Engenharia de Software Backend.

📧 Entre em contato: eniojr100@gmail.com <br>
🔗 LinkedIn: https://www.linkedin.com/in/enioeduardojr/ <br>
📷 Instagram: https://www.instagram.com/enio_juniorrr/ <br>
