# Agenda Medica

Aplicacao web de agenda medica para desafio tecnico, com autenticacao via SQLite e visualizacao de agendamentos vindos de uma mock API HTTP separada.

## Tecnologias
- Python 3.11+
- Flask 3.0.3
- SQLite (sqlite3 stdlib)
- requests
- Flask-WTF (CSRF no login)
- Tabulator (CDN)
- Docker e Docker Compose
- pytest e pytest-flask

## Executar com Docker
1. Copie .env.example para .env e ajuste se necessario.
2. Rode:

```bash
docker-compose up --build
```

3. Acesse http://localhost:5000

## Credenciais de teste
- Usuario: valor definido em TEST_USER_LOGIN no arquivo .env
- Senha: valor definido em TEST_USER_PASSWORD no arquivo .env

## Exemplos de uso
- Login valido: acesse /login, informe usuario e senha corretos, e voce sera redirecionado para a agenda.
- Busca na tabela: na tela principal, digite parte do nome do paciente, CPF ou medico para filtrar os agendamentos.
- Sem resultados: ao filtrar sem correspondencia, a interface exibe "Nenhum registro encontrado para esta busca.".

## Volume de dados mockados
- O endpoint da mock API fornece 50 exemplos de agendamentos gerados de forma deterministica.
- A tabela usa paginacao local com tamanhos de pagina modulaveis: 10, 25 e 50 linhas.

## Executar sem Docker
1. Crie e ative um ambiente virtual.
2. Instale dependencias:

```bash
pip install -r requirements.txt
```

3. Crie .env a partir de .env.example.
4. Inicialize banco:

```bash
python seed.py
```

5. Em outro terminal, suba a mock API:

```bash
python -m mock_api.app
```

6. Execute a aplicacao Flask:

```bash
flask run
```

## Limitacoes conhecidas
- SQLite não é ideal para alta concorrencia.
- Sessão Flask local sem armazenamento distribuido.
- Falta de inicialização sem docker unificada.
