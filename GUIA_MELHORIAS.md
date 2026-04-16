# 🚀 Guia Prático: Melhorando sua Aplicação Django

## 📊 Visão Geral da Aplicação Atual

Seu projeto é uma **loja digital** com:
- ✅ Autenticação de usuários
- ✅ Catálogo de produtos com categorias
- ✅ Carrinho de compras
- ✅ Sistema de pedidos
- ✅ E-mails de confirmação
- ✅ WebSockets (Channels)

---

## ⚠️ Problemas Identificados e Soluções

### **1. PERFORMANCE: N+1 Queries**

#### ❌ Problema
```python
# views.py - linha 111-140
ja_comprados = ItemPedido.objects.filter(
    pedido__usuario=request.user,
    pedido__status='pago'
).values_list('produto_id', flat=True)  # Query 1

relacionados = Produto.objects.filter(...)  # Query 2
if not relacionados.exists():  # Query 3
    relacionados = Produto.objects.filter(...)  # Query 4
```

**O que acontece**: Múltiplas consultas ao BD mesmo quando não necessário.

#### ✅ Solução
```python
from django.db.models import Exists, OuterRef, Q

def produto_detalhe(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id, status='ativo')

    # Query única otimizada
    ja_comprados = ItemPedido.objects.filter(
        pedido__usuario=request.user,
        pedido__status='pago'
    ).values_list('produto_id', flat=True)

    # Carrega tudo de uma vez
    relacionados = (
        Produto.objects
        .select_related('categoria')  # ← Carrega FK em 1 query
        .filter(status='ativo', categoria=produto.categoria)
        .exclude(id__in=ja_comprados)
        .exclude(id=produto.id)[:4]
    )

    if not relacionados:
        relacionados = (
            Produto.objects
            .select_related('categoria')
            .filter(status='ativo')
            .exclude(id=produto.id)
            .exclude(id__in=ja_comprados)[:4]
        )

    return render(request, 'produto_detalhe.html', {...})
```

---

### **2. CÓDIGO DUPLICADO: Verificação "já_comprou"**

#### ❌ Problema
```python
# Repetido em 3 lugares diferentes! 😱
ja_comprou = ItemPedido.objects.filter(
    pedido__usuario=request.user,
    pedido__status='pago',
    produto=produto
).exists()
```

#### ✅ Solução - Criar método no Model
```python
# models.py
class Produto(models.Model):
    # ... campos existentes ...
    
    def usuario_ja_comprou(self, usuario):
        """Verifica se o usuário já adquiriu este produto."""
        return ItemPedido.objects.filter(
            pedido__usuario=usuario,
            pedido__status=Pedido.Status.PAGO,
            produto=self
        ).exists()

# Agora na view fica simples:
ja_comprou = produto.usuario_ja_comprou(request.user)
```

---

### **3. SEGURANÇA: Falta Proteção contra Duplicação**

#### ❌ Problema
```python
# Usuario pode duplicar compra fazendo refresh na página
def confirmar_compra(request, produto_id):
    # Nada impede múltiplos POST
    pedido = Pedido.objects.create(...)
    ItemPedido.objects.create(...)
```

#### ✅ Solução - Usar Database Constraints
```python
# models.py
class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    preco = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        # ← ADICIONE ISTO: Impede duplicata
        unique_together = ('pedido', 'produto')
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'
```

#### ✅ Solução - Usar @transaction.atomic
```python
from django.db import transaction

@login_required
@transaction.atomic  # ← Garante que tudo salva ou nada salva
def confirmar_compra(request, produto_id):
    if request.method != 'POST':
        return redirect('produto_detalhe', produto_id=produto_id)

    produto = get_object_or_404(Produto, id=produto_id, status='ativo')

    # Bloqueia a linha enquanto processa
    ja_comprou = (
        ItemPedido.objects
        .select_for_update()
        .filter(
            pedido__usuario=request.user,
            pedido__status='pago',
            produto=produto
        )
        .exists()
    )

    if ja_comprou:
        messages.warning(request, 'Você já adquiriu este produto.')
        return redirect('minha_conta')

    pedido = Pedido.objects.create(
        usuario=request.user,
        status=Pedido.Status.PAGO,
        total=produto.preco
    )
    
    ItemPedido.objects.create(
        pedido=pedido,
        produto=produto,
        preco=produto.preco
    )

    enviar_email_confirmacao_compra(pedido)
    messages.success(request, f'Compra realizada!')
    
    return redirect('pedido_confirmado', pedido_id=pedido.id)
```

---

### **4. LOGGING: Substituir print() por Logging Apropriado**

#### ❌ Problema
```python
try:
    enviar_email_boas_vindas(usuario)
except Exception as e:
    print(f'Erro ao enviar e-mail: {e}')  # ← Desaparece em produção!
```

#### ✅ Solução
```python
# core/views.py - adicione no topo
import logging

logger = logging.getLogger(__name__)

# Agora:
try:
    enviar_email_boas_vindas(usuario)
except Exception as e:
    logger.error(f'Erro ao enviar e-mail para {usuario.email}: {e}', exc_info=True)
    messages.error(request, 'E-mail não foi enviado, mas conta criada com sucesso!')
```

**Configure em settings.py:**
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'core': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

### **5. CACHE: Categorias não mudam frequentemente**

#### ✅ Solução - Cache de Categorias
```python
from django.views.decorators.cache import cache_page
from django.core.cache import cache

def home(request):
    # Cache por 1 hora (3600 segundos)
    categorias = cache.get('categorias_ativas')
    
    if categorias is None:
        categorias = list(Categoria.objects.filter(ativa=True))
        cache.set('categorias_ativas', categorias, 3600)
    
    # ... resto do código

# Em models.py, limpar cache quando categoria for alterada:
class Categoria(models.Model):
    # ... campos ...
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        
        # Limpa cache quando categoria é salva
        cache.delete('categorias_ativas')
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        cache.delete('categorias_ativas')
        super().delete(*args, **kwargs)
```

---

### **6. FORMULÁRIOS: Validação customizada**

#### ✅ Solução - Adicionar Validações
```python
# core/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Produto

class FormCadastro(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        """Valida se e-mail já existe"""
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')
        return email

    def clean_username(self):
        """Valida comprimento mínimo"""
        username = self.cleaned_data.get('username')
        if len(username) < 3:
            raise forms.ValidationError('Mínimo 3 caracteres.')
        return username

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})
```

---

### **7. DJANGO ADMIN: Customizar para melhor UX**

#### ✅ Solução - Criar admin.py melhorado
```python
# core/admin.py
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Usuario, Categoria, Produto, Pedido, ItemPedido, Carrinho, ItemCarrinho

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name')
    ordering = ('-date_joined',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem', 'ativa', 'quantidade_produtos')
    list_editable = ('ordem', 'ativa')
    search_fields = ('nome',)
    prepopulated_fields = {'slug': ('nome',)}

    def quantidade_produtos(self, obj):
        return obj.produtos.count()
    quantidade_produtos.short_description = 'Produtos'

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'preco_original', 'categoria', 'status', 'destaque', 'imagem_thumb')
    list_filter = ('status', 'destaque', 'categoria', 'criado_em')
    search_fields = ('nome', 'descricao')
    readonly_fields = ('slug', 'criado_em', 'atualizado_em', 'imagem_preview')
    prepopulated_fields = {'slug': ('nome',)}
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'slug', 'categoria')
        }),
        ('Descrição', {
            'fields': ('resumo', 'descricao')
        }),
        ('Preço', {
            'fields': ('preco', 'preco_original')
        }),
        ('Imagem', {
            'fields': ('imagem', 'imagem_preview')
        }),
        ('Status', {
            'fields': ('status', 'destaque')
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )

    def imagem_preview(self, obj):
        if obj.imagem:
            return mark_safe(f'<img src="{obj.imagem.url}" width="200" />')
        return 'Sem imagem'
    imagem_preview.short_description = 'Prévia'

    def imagem_thumb(self, obj):
        if obj.imagem:
            return mark_safe(f'<img src="{obj.imagem.url}" width="50" />')
        return '-'
    imagem_thumb.short_description = 'Imagem'

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'status', 'total', 'criado_em')
    list_filter = ('status', 'criado_em')
    search_fields = ('usuario__username', 'usuario__email', 'id')
    readonly_fields = ('usuario', 'total', 'criado_em', 'atualizado_em', 'itens_display')

    def itens_display(self, obj):
        return ', '.join([f'{i.produto.nome} (R$ {i.preco})' for i in obj.itens.all()])
    itens_display.short_description = 'Itens'

@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'produto', 'preco')
    list_filter = ('pedido__status', 'pedido__criado_em')
    search_fields = ('pedido__id', 'produto__nome')
    readonly_fields = ('pedido', 'produto', 'preco')
```

---

### **8. TESTES: Criar testes unitários**

#### ✅ Solução - Arquivo de testes
```python
# core/tests.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Categoria, Produto, Pedido, ItemPedido

User = get_user_model()

class ProdutoTestCase(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nome='Python')
        self.produto = Produto.objects.create(
            nome='Curso Django',
            categoria=self.categoria,
            preco=99.90,
            status='ativo'
        )

    def test_slug_auto_generated(self):
        """Testa se slug é gerado automaticamente"""
        self.assertEqual(self.produto.slug, 'curso-django')

    def test_desconto_calculo(self):
        """Testa cálculo de percentual de desconto"""
        self.produto.preco_original = 199.90
        self.assertTrue(self.produto.tem_desconto)
        self.assertEqual(self.produto.percentual_desconto, 50)

class CompraTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.categoria = Categoria.objects.create(nome='Test')
        self.produto = Produto.objects.create(
            nome='Produto Teste',
            categoria=self.categoria,
            preco=50.00,
            status='ativo'
        )
        self.client = Client()

    def test_usuario_ja_comprou(self):
        """Testa verificação de compra anterior"""
        pedido = Pedido.objects.create(
            usuario=self.user,
            status='pago',
            total=50.00
        )
        ItemPedido.objects.create(
            pedido=pedido,
            produto=self.produto,
            preco=50.00
        )
        
        self.assertTrue(self.produto.usuario_ja_comprou(self.user))

    def test_comprar_produto_requer_login(self):
        """Testa se compra requer autenticação"""
        response = self.client.get(f'/produto/{self.produto.id}/comprar/')
        self.assertEqual(response.status_code, 302)  # Redirect
```

**Rodar testes:**
```bash
python manage.py test core
```

---

### **9. DOCSTRINGS: Documentar código**

#### ✅ Solução - Adicionar documentação
```python
def produto_detalhe(request, produto_id):
    """
    Exibe detalhes de um produto e produtos relacionados.
    
    Args:
        request: Objeto HttpRequest
        produto_id (int): ID do produto
        
    Returns:
        HttpResponse: Página com detalhes do produto
        
    Raises:
        Http404: Se produto não existir ou estiver inativo
    """
    produto = get_object_or_404(Produto, id=produto_id, status='ativo')
    
    # Obtém IDs dos produtos já comprados pelo usuário
    ja_comprados = (
        ItemPedido.objects
        .filter(pedido__usuario=request.user, pedido__status='pago')
        .values_list('produto_id', flat=True)
    )
    
    # ... resto do código
```

---

### **10. ESTRUTURA: Organizar views grandes**

#### ✅ Solução - Separar em múltiplos arquivos
```
core/
├── views/
│   ├── __init__.py
│   ├── produto.py      # Views de produtos
│   ├── carrinho.py     # Views de carrinho
│   ├── pedido.py       # Views de pedidos
│   ├── auth.py         # Views de autenticação
│   └── conta.py        # Views de conta do usuário
├── managers.py         # Query managers customizados
├── services.py         # Lógica de negócio
└── ...
```

**Exemplo - core/managers.py:**
```python
from django.db import models

class ProdutoQuerySet(models.QuerySet):
    def ativos(self):
        """Retorna apenas produtos ativos"""
        return self.filter(status='ativo')
    
    def com_desconto(self):
        """Retorna apenas produtos com desconto"""
        return self.exclude(preco_original__isnull=True)
    
    def destaques(self):
        """Retorna apenas produtos em destaque"""
        return self.filter(destaque=True)

class ProdutoManager(models.Manager):
    def get_queryset(self):
        return ProdutoQuerySet(self.model, using=self._db)
    
    def ativos(self):
        return self.get_queryset().ativos()
    
    def com_desconto(self):
        return self.get_queryset().com_desconto()
```

Uso:
```python
# Muito mais legível!
produtos = Produto.objects.ativos().com_desconto()
```

---

## 📚 Recursos Recomendados

1. **Django Docs Oficiais**: https://docs.djangoproject.com/
2. **Two Scoops of Django**: Best practices do Django
3. **Django Design Patterns**: https://github.com/HackSoftware/Django-Styleguide
4. **Performance**: https://docs.djangoproject.com/en/stable/topics/db/optimization/

---

## 🎯 Próximos Passos

1. ✅ Implemente `select_related()` e `prefetch_related()`
2. ✅ Crie métodos no Model para evitar duplicação
3. ✅ Configure logging apropriado
4. ✅ Adicione `@transaction.atomic` em operações críticas
5. ✅ Implemente cache para dados estáticos
6. ✅ Customize Django Admin
7. ✅ Escreva testes unitários
8. ✅ Adicione docstrings

---

**Quer que eu implemente alguma dessas melhorias no seu código?**
