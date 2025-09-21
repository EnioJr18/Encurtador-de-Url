# 🔗 Encurtador de URL com Flask

Um encurtador de URLs simples, funcional e elegante, construído com Python e o micro-framework Flask. Este projeto foi desenvolvido como uma demonstração prática de habilidades full-stack, cobrindo desde a lógica do back-end e manipulação de banco de dados até a criação de uma interface de usuário interativa no front-end.

## 📸 Demonstração Visual

<p align="center">
  <img src="https://github.com/EnioJr18/Encurtador-de-Url/issues/1#issue-3437845808" alt="Demonstração animada do Encurtador de URL" width="80%">
</p>

## ✨ Funcionalidades

- **Encurtamento de URLs:** Transforma URLs longas e complexas em links curtos e fáceis de compartilhar.
- **Redirecionamento Automático:** Acessar um link curto redireciona instantaneamente para a URL original.
- **Listagem de Links:** Uma página dedicada para visualizar todos os links que já foram encurtados pela aplicação.
- **Botão "Copiar":** Funcionalidade em JavaScript que permite copiar a URL curta para a área de transferência com um único clique, incluindo feedback visual.
- **Interface Responsiva:** Design limpo e adaptável para uma boa experiência tanto em desktops quanto em dispositivos móveis.

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias:

#### **Back-end**
* **Python 3**
* **Flask:** Um micro-framework para a criação da aplicação web e da API.
* **SQLAlchemy:** ORM para interação com o banco de dados de forma pythonica.
* **Gunicorn:** Servidor WSGI para rodar a aplicação em produção.

#### **Front-end**
* **HTML5**
* **CSS3**
* **JavaScript (Vanilla JS):** Para manipulação do DOM e interatividade (botão de copiar).

#### **Banco de Dados**
* **SQLite:** Utilizado para o ambiente de desenvolvimento local.
* **PostgreSQL:** Utilizado no ambiente de produção.

#### **Deploy**
* **Git & GitHub:** Para versionamento de código e integração com a plataforma de deploy.

## 🚀 Como Rodar o Projeto Localmente

Siga os passos abaixo para executar o projeto em sua máquina.

**Pré-requisitos:**
* **Python 3.10+**
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

4.  **Crie o banco de dados:**
    ```bash
    # Inicie o shell do Flask
    flask shell
    ```
    Dentro do shell, execute os seguintes comandos Python:
    ```python
    >>> from app import db
    >>> db.create_all()
    >>> exit()
    ```

5.  **Execute a aplicação:**
    ```bash
    flask run
    ```

6.  Abra seu navegador e acesse `http://127.0.0.1:5000`.

## 👨‍💻 Autor

Feito com ❤️ por **Enio Junior**.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Enio_Junior-0077B5?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/enioeduardojr/)
[![GitHub](https://img.shields.io/badge/GitHub-EnioJr18-181717?style=for-the-badge&logo=github)](https://github.com/EnioJr18)
[![E-mail](https://img.shields.io/badge/Email)](eniojr100@gmail.com)
[![Instagram](https://img.shields.io/badge/Instagram)](https://www.instagram.com/enio_jr100)
