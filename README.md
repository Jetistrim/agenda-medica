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

5. Execute app:

```bash
flask run
```

## Decisoes tecnicas
- Mock API separada para simular servico externo de agendamentos.
- Senhas armazenadas somente em hash com werkzeug.security.
- Usuario inicial carregado de variaveis TEST_USER_* para evitar credenciais hardcoded em Python.
- Tabela no frontend com Tabulator 6.3.0 versionado localmente em static/vendor para busca e filtragem rapidas.

## Limitacoes conhecidas
- Sem HTTPS na execucao local.
- SQLite nao e ideal para alta concorrencia.
- Sessao Flask local sem armazenamento distribuido.
