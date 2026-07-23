# copilot-instructions.md — Agenda Médica

---

## 1. Escopo do Projeto

**O que é:** Aplicação web de agenda médica para desafio técnico avaliativo (TimeSaver).
**Para quem:** Avaliadores técnicos da TimeSaver; usuário final é um médico/recepcionista que faz login e consulta agendamentos.
**Problema que resolve:** Visualização autenticada de agendamentos médicos com busca/filtro e integração com API de dados.

**Restrições conhecidas:**
- Prazo extremamente curto (entrega até 23/07/2026 — candidato solo).
- Stack fixada pelo desafio: Python + Flask, SQLite, Docker.
- Projeto avaliativo: clareza e explicabilidade do código têm peso igual à funcionalidade.

**Fora de escopo (não implementar em nenhuma fase deste projeto):**
- OAuth / SSO / autenticação multi-fator.
- Banco de dados além de SQLite.
- Cache distribuído, filas assíncronas, WebSockets.
- RBAC avançado (perfis múltiplos).
- Internacionalização / acessibilidade avançada.
- Deploy em nuvem (apenas Docker local).
- Paginação server-side (Tabulator lida no frontend).

---

## 2. Requisitos Funcionais

| # | Requisito | Status |
|---|-----------|--------|
| RF-01 | Tela de login com campos usuário/e-mail e senha | ✅ Materializado |
| RF-02 | Validação de credenciais via SQLite; mensagem clara em caso de falha | ✅ Materializado |
| RF-03 | Redirecionamento para tela principal após login válido | ✅ Materializado |
| RF-04 | Requisição HTTP à API simulada para buscar agendamentos | ✅ Materializado |
| RF-05 | Tabela Tabulator com colunas: data, horário, paciente, CPF, médico, especialidade, convênio, status | ✅ Materializado |
| RF-06 | Filtro/busca por paciente, CPF ou médico na tabela | ✅ Materializado |
| RF-07 | Mensagem quando não há agendamentos | ✅ Materializado |
| RF-08 | Campo de busca na tela principal (CPF, nome ou identificador) com feedback de "nenhum registro encontrado" | ✅ Materializado |
| RF-09 | Entradas vazias ou inválidas tratadas sem erro interno | ✅ Materializado |
| RF-10 | API simulada como serviço separado (mock HTTP endpoint) | ✅ Materializado |
| RF-11 | Script/seed de criação do banco e usuário de teste | ✅ Materializado |

---

## 3. Requisitos Não Funcionais

| Requisito | Critério verificável (pass/fail) |
|-----------|----------------------------------|
| Segurança de credenciais | Senhas armazenadas com hash (werkzeug `generate_password_hash`); nenhuma senha em texto plano no banco ou nos logs |
| Sem segredos no repositório | `.env` listado no `.gitignore`; `.env.example` presente com valores fictícios; `flask run` não sobe sem `.env` (ou fallback explícito) |
| Tratamento de falhas | Todos os 6 cenários da Parte 2 retornam mensagem amigável ao usuário e log estruturado; nenhum resulta em HTTP 500 não tratado ou traceback exposto |
| Execução com um comando | `docker-compose up --build` sobe a aplicação + mock API + banco inicializado, sem intervenção manual |
| Legibilidade | Nenhuma função com mais de 40 linhas; nenhum bloco `except: pass`; nenhuma variável nomeada `x`, `tmp`, `data2` |
| Testabilidade mínima | Ao menos 2 testes automatizados (pytest) passando com `pytest` sem dependência de serviço externo real |

---

## 4. Stack Aprovada

| Camada | Ferramenta | Papel |
|--------|------------|-------|
| Runtime | Python 3.11+ | Linguagem principal |
| Framework web | Flask | Roteamento, sessão, templates |
| Banco de dados | SQLite (via `sqlite3` stdlib ou Flask-SQLAlchemy) | Persistência de usuários |
| Hash de senha | `werkzeug.security` | `generate_password_hash` / `check_password_hash` |
| HTTP client | `requests` | Chamada à mock API |
| Mock API | Flask (serviço separado) | Endpoint HTTP que retorna agendamentos mockados |
| Frontend tabela | Tabulator (CDN) | Renderização de tabela com filtros |
| Templates | Jinja2 (incluso no Flask) | HTML server-side |
| Containerização | Docker + docker-compose | Orquestração de serviços |
| Testes | pytest + pytest-flask | Testes automatizados |
| Variáveis de ambiente | python-dotenv | Leitura de `.env` |

**Política de Dependências:** Nenhuma biblioteca fora desta tabela deve ser adicionada sem apresentar, na mesma mensagem: (1) justificativa, (2) impacto no build, (3) alternativa sem nova dependência, (4) pedido explícito de aprovação.

---

## 5. Fase Atual e Comportamento Esperado da IA

### **Fase Atual: Fase 2 — Testes e blindagem [RIGOR: ALTO] ✅ Concluída**

#### Fase 0 — Descoberta e MVP lógico [RIGOR: BAIXO] ✅ Concluída
**Critério de saída atingido:** lógica de login, busca de agendamentos e integração HTTP definidas e validadas.

#### **Fase 1 — Contratos e arquitetura [RIGOR: MÉDIO] ✅ Concluída**
**Foco da IA:** estrutura de camadas, tratamento de todos os cenários de falha, validação de entrada, logging.
**A IA NÃO deve:** criar testes de integração complexos, focar em performance, adicionar funcionalidades além do escopo.
**A IA DEVE:**
- Isolar I/O (banco, HTTP) da lógica de negócio.
- Usar tipagem básica (type hints em todas as funções públicas).
- Retornar erros tipados ou lançar exceções documentadas; nunca `except: pass`.
- Logar todos os erros com campos mínimos: `timestamp`, `level`, `event`, `error_type`.

**Critério de saída verificável:**
- [x] Todos os 6 cenários de falha da Parte 2 retornam resposta HTTP controlada (não 500 nu).
- [x] Nenhum `print()` em código de produção (usar `app.logger`).
- [x] `docker-compose up --build` sobe tudo sem erro.
- [x] Seed cria usuário de teste e banco na primeira execução.

#### **Fase 2 — Testes e blindagem [RIGOR: ALTO] ✅ Concluída**
**Foco da IA:** cobertura de testes, mocks de HTTP e banco.
**Critério de saída:**
- [x] `pytest` passa 100% dos testes.
- [x] Login válido, login inválido, retorno vazio da API e falha da API cobertos por teste.
- [x] Nenhum teste bate em SQLite real nem em HTTP real.

#### Fase 3 — Produtização [RIGOR: MÁXIMO] 🔲 Contrato (fora do escopo deste desafio)

---

## 6. Arquitetura e Separação de Responsabilidades

### Estrutura de diretórios esperada

```
agenda-medica/
├── app/
│   ├── __init__.py          # Application Factory (create_app)
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py        # /login, /logout
│   ├── agenda/
│   │   ├── __init__.py
│   │   └── routes.py        # / (tela principal), /api/agendamentos
│   ├── services/
│   │   ├── db.py            # Operações de banco (get_user_by_login)
│   │   └── api_client.py    # Chamada HTTP à mock API
│   ├── models.py            # Definição de tabelas (SQL puro ou SQLAlchemy)
│   └── templates/
│       ├── login.html
│       └── agenda.html
├── mock_api/
│   ├── app.py               # Flask app da mock API
│   └── data.py              # Dados mockados
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_agenda.py
├── seed.py                  # Cria banco e insere usuário de teste
├── .env.example
├── .gitignore
├── Dockerfile
├── Dockerfile.mock
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### Regra de ouro — o que NUNCA misturar no mesmo arquivo:
- Lógica de banco de dados e lógica de roteamento HTTP **não devem** estar no mesmo arquivo.
- Chamada HTTP à API externa e renderização de template **não devem** estar na mesma função.
- Configuração de credenciais **não deve** estar hardcoded em nenhum arquivo Python.
- Seed de dados e código de produção **não devem** compartilhar o mesmo módulo executável.

---

## 7. Padrões de Código

### Geral (Python / Flask)
- Todo arquivo Python **deve** seguir PEP 8. Linhas máx. 100 chars.
- Toda função pública **deve** ter type hints nos parâmetros e retorno.
- Toda função pública **deve** retornar erro tipado ou lançar exceção documentada — nunca `except: pass` ou `except Exception` sem log.
- `print()` **não deve** aparecer em código de produção. Usar `app.logger.info/warning/error`.
- Variáveis **devem** ter nomes descritivos em inglês. Proibido: `x`, `tmp`, `data2`, `res`.
- Imports **devem** ser organizados: stdlib → third-party → local, separados por linha em branco.

### Flask — Application Factory
- A aplicação **deve** usar o padrão Application Factory (`create_app()` em `app/__init__.py`).
- Blueprints **devem** ser usados para separar `auth` e `agenda`.
- `SECRET_KEY` **deve** vir de variável de ambiente; **não deve** ter valor padrão inseguro em produção.

### Segurança de autenticação
- Senhas **devem** ser armazenadas com `generate_password_hash(password, method='pbkdf2:sha256')`.
- A verificação **deve** usar `check_password_hash`; nunca comparação direta de string.
- Sessão Flask **deve** ser usada para controle de login; rotas protegidas **devem** verificar `session.get('user_id')` e redirecionar para `/login` se ausente.
- Formulário de login **deve** usar CSRF protection mínima via token de sessão ou Flask-WTF.

### Tratamento de erros — critérios verificáveis
| Cenário | Comportamento esperado | HTTP esperado |
|---------|------------------------|---------------|
| Credenciais inválidas | Flash message "Usuário ou senha inválidos." + renderiza login | 200 (form reload) |
| API indisponível (timeout/ConnectionError) | Exibe banner "Serviço de agendamentos temporariamente indisponível." + log `error_type=API_UNAVAILABLE` | 200 (agenda com banner) |
| Resposta inválida da API (JSON malformado / campos ausentes) | Exibe banner "Dados recebidos estão incompletos." + log `error_type=API_INVALID_RESPONSE` | 200 (agenda com banner) |
| Nenhum agendamento encontrado | Tabela exibe "Nenhum agendamento encontrado." (mensagem Tabulator) | 200 |
| Busca sem resultado | Mensagem inline "Nenhum registro encontrado para esta busca." | 200 |
| Erro de banco de dados | Página de erro amigável "Erro interno. Tente novamente." + log `error_type=DB_ERROR` | 500 tratado (handler registrado) |

### Logging — contrato mínimo de campos
Todo log de erro **deve** conter:
```python
app.logger.error("event=..., error_type=..., detail=...", exc_info=True)
```
Campos obrigatórios: `event` (ação que falhou), `error_type` (código de categoria), `detail` (mensagem da exceção).

---

## 8. Segurança e Observabilidade

- `.env` **deve** estar no `.gitignore`. Proibido commitar `.env` com valores reais.
- `.env.example` **deve** existir com valores fictícios para todas as variáveis usadas.
- Variáveis obrigatórias: `SECRET_KEY`, `DATABASE_URL` (ou `DATABASE_PATH`), `MOCK_API_URL`.
- Seed **deve** usar senha fictícia (`senha123` ou similar), documentada no README.
- `DEBUG=True` **não deve** estar ativo em imagem Docker de entrega; usar variável de ambiente.
- SQL **deve** usar parâmetros bindados (placeholders `?`) — nunca concatenação de string em queries.
- Headers de segurança básicos (X-Content-Type-Options, X-Frame-Options) **deveriam** ser adicionados via `@app.after_request` se o tempo permitir.

---

## 9. Padrão de Erros de API e UI

### API interna (endpoint `/api/agendamentos`)
Formato de resposta de erro:
```json
{ "error": "CODIGO_ERRO", "message": "Texto amigável para o usuário" }
```

Códigos usados: `API_UNAVAILABLE`, `API_INVALID_RESPONSE`, `DB_ERROR`, `NO_RESULTS`.

### UI
- Erros **devem** ser exibidos via Flash messages (banner único no topo da página).
- Nenhuma página **deve** quebrar visualmente por causa de um erro; o layout base **deve** sempre renderizar.
- Mensagens técnicas (stack trace, SQL) **não devem** aparecer para o usuário em nenhuma circunstância.

---

## 10. Testes

🔲 **Contrato — ativado na Fase 2, mas mínimo obrigatório pelo desafio:**

A entrega **deve** conter ao menos 2 testes automatizados com `pytest`:

| Teste | Tipo | Mock necessário |
|-------|------|-----------------|
| Login com credenciais válidas → redirect para `/` | Integração (Flask test client) | SQLite em memória |
| Login com credenciais inválidas → flash de erro | Integração (Flask test client) | SQLite em memória |
| Busca de paciente inexistente → resposta sem erro interno | Integração | Mock HTTP da API |
| Falha da API (timeout) → banner amigável, sem 500 | Integração | `requests` mockado com `unittest.mock` |

- Testes **não devem** depender de SQLite de arquivo real nem de HTTP real.
- `conftest.py` **deve** fornecer `app` e `client` fixtures com banco em memória.

---

## 11. CI/CD e Gates de Qualidade

🔲 **Contrato — fora do escopo deste desafio.** Placeholder para futuro.

Quando ativado:
- [ ] `pytest` verde é bloqueante para merge.
- [ ] `flake8` ou `ruff` sem erros é bloqueante.

---

## 12. Documentação Operacional

### README deve conter:
1. Descrição breve da solução (2-3 linhas).
2. Tecnologias utilizadas (lista com versões).
3. Instruções para executar com Docker: `docker-compose up --build` → acessar `http://localhost:5000`.
4. Credenciais do usuário de teste (usuário e senha).
5. Como executar sem Docker (passos com `venv` e `python seed.py`).
6. Decisões técnicas (mock API separada, hash de senha, Tabulator via CDN).
7. Limitações conhecidas (ex.: sem HTTPS, SQLite não concorrente, sessão em memória).

### Arquivos obrigatórios na raiz:
- `README.md`
- `.env.example`
- `requirements.txt`
- `docker-compose.yml`
- `Dockerfile`
- `seed.py`

---

## 13. Checklist de Nova Sessão com a IA

Antes de qualquer prompt técnico, responda:
1. **Fase atual** (sempre Fase 1 para este projeto) + última decisão relevante tomada.
2. **Impacto esperado** da mudança que está sendo pedida (arquivos afetados).
3. A IA **deve** apresentar um plano de 3-5 passos antes de escrever código para qualquer tarefa não trivial.
4. A IA **não deve** implementar nada além do escopo da fase atual sem aprovação explícita.
5. Se uma dependência nova for sugerida, a IA **deve** seguir a Política de Dependências (seção 4) antes de adicioná-la.
6. Antes de assumir qualquer decisão de arquitetura ou regra de negócio não explícita: inspecionar `requirements.txt`, `app/__init__.py` e arquivos existentes; se a lacuna persistir, parar e perguntar.
7. Toda mudança proposta **deve** citar explicitamente os arquivos afetados.
8. Nenhuma credencial, mesmo fictícia, **deve** ser hardcoded em arquivo Python.