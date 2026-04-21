# DigitalHub

E-commerce full stack com Django REST API, React + Vite e SQLite. Inclui catálogo de produtos, carrinho de compras e gerenciamento de pedidos.

## Tecnologias

**Backend:**
- Django 4.x
- Django REST Framework
- SQLite
- Channels (WebSockets)

**Frontend:**
- React 18
- Vite
- Zustand (state management)
- Axios (HTTP client)

## Requisitos

- Python 3.8+
- Node.js 16+
- npm ou yarn

## Instalação

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd DigitalHub
```

### 2. Configurar o Backend (Django)

Criar e ativar o ambiente virtual:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

Instalar dependências:

```bash
pip install -r requirements.txt
```

Executar migrações:

```bash
python manage.py migrate
```

Criar superusuário (opcional):

```bash
python manage.py createsuperuser
```

### 3. Configurar o Frontend (React)

Instalar dependências:

```bash
npm install
```

## Executar o Projeto

### Backend (Django)

Com o ambiente virtual ativado:

```bash
python manage.py runserver
```

O servidor estará disponível em `http://localhost:8000`

A API estará em `http://localhost:8000/api/`

O admin em `http://localhost:8000/admin/`

### Frontend (React)

Em outro terminal:

```bash
npm run dev
```

O projeto React estará em `http://localhost:5173`

## Estrutura do Projeto

```
DigitalHub/
├── core/                    # App Django principal
│   ├── models.py           # Modelos (Produto, Categoria, Pedido, etc)
│   ├── api_views.py        # Endpoints da API
│   ├── api_urls.py         # Rotas da API
│   ├── serializers.py      # Serializers DRF
│   ├── views.py            # Views das templates
│   └── templates/          # Templates HTML
│
├── django1/                # Configurações Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── src/                    # Código React
│   ├── main.jsx           # Entry point
│   ├── components/        # Componentes React
│   └── pages/
│
├── manage.py              # CLI Django
├── requirements.txt       # Dependências Python
├── package.json          # Dependências Node.js
└── vite.config.js        # Configuração Vite
```

## Endpoints da API

Os principais endpoints REST estão em `core/api_urls.py`. Exemplos:

- `GET /api/produtos/` - Listar produtos
- `GET /api/categorias/` - Listar categorias
- `POST /api/carrinho/` - Criar carrinho
- `POST /api/pedidos/` - Criar pedido

## Testes

Executar testes:

```bash
python manage.py test
```

Ou diretamente:

```bash
python -m pytest tests/
```

## Comandos Úteis

Coletar arquivos estáticos:

```bash
python manage.py collectstatic
```

Fazer dump do banco de dados:

```bash
python manage.py dumpdata > db_backup.json
```

Carregar dados:

```bash
python manage.py loaddata db_backup.json
```

## Notas

- O banco de dados SQLite é local (`db.sqlite3`)
- Arquivos de mídia são armazenados em `media/`
- Arquivos estáticos estão em `staticfiles/`
- O frontend consome a API via Axios
- Zustand gerencia estado global do React

