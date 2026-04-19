# 🧪 Testes do DigitalHub

Pasta contendo uma suíte completa de testes automatizados para o projeto DigitalHub.

## 📋 Arquivos de Teste

### 1. **test_database.py** - Testes de Banco de Dados
Valida conexão, migrações, modelos e integridade de dados.

**Testes inclusos:**
- ✅ Conexão com banco de dados
- ✅ Existência de todas as tabelas
- ✅ Criação de categorias
- ✅ Criação de produtos
- ✅ Gestão de estoque
- ✅ Carrinho e pedidos
- ✅ Integridade referencial (chaves estrangeiras)

**Como executar:**
```bash
python manage.py test tests.test_database
```

---

### 2. **test_login.py** - Testes de Autenticação e Login
Verifica registro, login, logout e permissões de usuário.

**Testes inclusos:**
- ✅ Criação de usuários
- ✅ Hash de senhas
- ✅ Validação de emails
- ✅ Proteção contra nomes duplicados
- ✅ Autenticação (login/logout)
- ✅ Sessões de usuário
- ✅ Reset de senha
- ✅ Permissões (admin/regular)

**Como executar:**
```bash
python manage.py test tests.test_login
```

---

### 3. **test_produtos.py** - Testes de Produtos
Valida criação, listagem, filtros e detalhes de produtos.

**Testes inclusos:**
- ✅ Criação de produtos simples e completos
- ✅ Múltiplos produtos em mesma categoria
- ✅ Filtro por categoria
- ✅ Filtro por faixa de preço
- ✅ Busca por título (case-insensitive)
- ✅ Filtros combinados
- ✅ Gestão de estoque
- ✅ Validação de preços
- ✅ Ordenação por preço (ascendente/descendente)

**Como executar:**
```bash
python manage.py test tests.test_produtos
```

---

### 4. **test_carrinho.py** - Testes de Carrinho
Valida operações do carrinho de compras.

**Testes inclusos:**
- ✅ Criação de carrinho
- ✅ Carrinho vazio inicialmente
- ✅ Adição de itens
- ✅ Adição de múltiplos itens
- ✅ Remoção de itens
- ✅ Atualização de quantidade
- ✅ Proteção contra quantidade zero
- ✅ Status do carrinho (ativo/inativo)
- ✅ Consolidação de itens duplicados

**Como executar:**
```bash
python manage.py test tests.test_carrinho
```

---

### 5. **test_ui_contrast.py** - Testes de Acessibilidade UI
Verifica contraste de cores de texto nos templates.

**Testes inclusos:**
- ✅ Contraste de cores em descrições de produtos
- ✅ Contraste em subtítulos
- ✅ Contraste em textos da navbar
- ✅ Visibilidade de ícones
- ✅ Estados active/hover diferenciados

**Como executar:**
```bash
python test_ui_contrast.py
```

---

## 🚀 Executar Todos os Testes

### Opção 1: Executar todos os testes Django
```bash
python manage.py test tests
```

### Opção 2: Executar testes específicos
```bash
# Apenas banco de dados
python manage.py test tests.test_database

# Apenas login
python manage.py test tests.test_login

# Apenas produtos
python manage.py test tests.test_produtos

# Apenas carrinho
python manage.py test tests.test_carrinho
```

### Opção 3: Executar com verbosidade
```bash
python manage.py test tests --verbosity=2
```

---

## 📊 Cobertura de Testes

| Componente | Testes | Status |
|-----------|--------|--------|
| Banco de Dados | 7 | ✅ |
| Autenticação | 8 | ✅ |
| Produtos | 9 | ✅ |
| Carrinho | 9 | ✅ |
| UI/Acessibilidade | 5 | ✅ |
| **TOTAL** | **38** | **✅** |

---

## 🔍 O que é testado

### Funcionalidade
- ✅ Criação e modificação de dados
- ✅ Relacionamentos entre modelos
- ✅ Filtros e buscas
- ✅ Validações

### Autenticação
- ✅ Registro de usuários
- ✅ Login/Logout
- ✅ Permissões

### Performance
- ✅ Operações básicas do carrinho
- ✅ Queries otimizadas
- ✅ Filtros eficientes

### Acessibilidade
- ✅ Contraste de cores
- ✅ Legibilidade de texto
- ✅ Visibilidade de elementos

---

## 🛠️ Configuração do Ambiente de Teste

Os testes usam um banco de dados de teste separado que é criado e destruído automaticamente.

**Configuração:**
- Banco de dados: SQLite em memória (`:memory:`)
- Isolamento: Cada teste roda em transação separada
- Limpeza: Automática após cada teste

---

## 📝 Formato de Saída dos Testes

Exemplo de saída esperada:
```
======================================================================
✅ TESTES DE BANCO DE DADOS - DIGITALHUB
======================================================================

test_categoria_creation (tests.test_database.TestCategoriaModel) ... ok
test_categoria_string_representation (tests.test_database.TestCategoriaModel) ... ok
test_database_connection (tests.test_database.TestDatabaseConnection) ... ok
...

======================================================================
✅ TODOS OS TESTES DE BANCO DE DADOS PASSARAM!
======================================================================
```

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'tests'"
**Solução:** Certifique-se de que está na pasta raiz do projeto

### Erro: "ImproperlyConfigured: Requested setting DATABASES"
**Solução:** Execute com `python manage.py test` em vez de `python -m unittest`

### Banco de dados ainda bloqueado?
**Solução:** Remova `db.sqlite3` e execute as migrações novamente

---

## 📚 Recursos Adicionais

- [Django Testing Docs](https://docs.djangoproject.com/en/6.0/topics/testing/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)

---

**Última atualização**: 18 de abril de 2026

**Mantido por**: Equipe DigitalHub
