# Controle de Gastos — Trabalho Avaliativo de Flask

## Tema do projeto
Aplicação web para **controle pessoal de gastos**, permitindo que o usuário
cadastre, visualize, edite e remova despesas do dia a dia (mercado, contas,
lazer, transporte etc.), acompanhando o total gasto e filtrando por categoria.

## Funcionalidades implementadas
- CRUD completo de gastos (Create, Read, Update, Delete) usando **Flask-SQLAlchemy**
  com banco de dados **SQLite**.
- 7 rotas diferentes, incluindo uma rota dinâmica com parâmetro na URL
  (`/gasto/<int:id>`).
- Dashboard inicial com total de gastos cadastrados e soma geral.
- Listagem de gastos com **filtro por categoria**, cuja última escolha fica
  salva na **session** do usuário.
- Formulário de cadastro e de edição (mesma tela, mesma rota tratando
  **GET e POST**), com **validação server-side** de todos os campos.
- **Cookie** de preferência de tema (claro/escuro), persistente por 1 ano.
- **Session** usada também para contar quantos gastos foram cadastrados
  durante a sessão atual do navegador.
- **Flash messages** para sucesso/erro em cadastro, edição e remoção.
- Templates com **herança** (`base.html`), variáveis, laços (`for`) e
  condicionais (`if`) do Jinja2.
- Estilização com **CSS** próprio (incluindo tema escuro) e **JavaScript**
  (confirmação de exclusão, formatação de valor e some automático das
  mensagens flash).

## Estrutura do projeto
```
controle_gastos/
├── app.py                # Rotas e lógica da aplicação
├── models.py              # Model Gasto (SQLAlchemy)
├── requirements.txt        # Dependências (gerado com pip freeze)
├── static/
│   ├── css/style.css
│   └── js/script.js
└── templates/
    ├── base.html
    ├── index.html
    ├── listar.html
    ├── detalhe.html
    └── form.html
```

## Como executar o projeto

1. Clone o repositório e entre na pasta do projeto:
   ```bash
   git clone <url-do-repositorio>
   cd controle_gastos
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux / macOS
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute a aplicação:
   ```bash
   python app.py
   ```

5. Acesse no navegador:
   ```
   http://127.0.0.1:5000
   ```

O banco de dados SQLite (`gastos.db`) é criado automaticamente na primeira
execução, na mesma pasta do projeto.

## Modelo de dados (Gasto)
| Campo             | Tipo    | Descrição                                   |
|-------------------|---------|-----------------------------------------------|
| id                | Integer | Identificador único (chave primária)          |
| descricao         | String  | Descrição do gasto                            |
| valor             | Float   | Valor gasto em reais                          |
| categoria         | String  | Categoria (Alimentação, Transporte, etc.)     |
| data              | Date    | Data em que o gasto ocorreu                   |
| forma_pagamento   | String  | Dinheiro, Pix, Cartão de Crédito/Débito, etc. |
