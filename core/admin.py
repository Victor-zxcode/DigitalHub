from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Produto, Categoria, Pedido, ItemPedido, Carrinho, ItemCarrinho


admin.site.register(ItemPedido)
admin.site.register(ItemCarrinho)


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('username', 'email', 'first_name', 'last_name')
        }),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

    list_display = ('username', 'email', 'nome_completo', 'status_badge', 'data_registro')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined')

    def nome_completo(self, obj):
        return obj.get_full_name() or obj.username
    nome_completo.short_description = 'Nome Completo'

    def status_badge(self, obj):
        if obj.is_superuser:
            return '👑 Admin'
        elif obj.is_staff:
            return '👤 Staff'
        else:
            return '✓ Ativo' if obj.is_active else '✗ Inativo'
    status_badge.short_description = 'Status'

    def data_registro(self, obj):
        return obj.date_joined.strftime('%d/%m/%Y %H:%M')
    data_registro.short_description = 'Registrado em'


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Informações', {
            'fields': ('nome', 'slug', 'ordem')
        }),
        ('Exibição', {
            'fields': ('ativa', 'icone', 'icone_lucide')
        }),
    )

    list_display = ('nome', 'quantidade_produtos', 'ordem', 'ativa', 'icone_lucide')
    list_filter = ('ativa', 'ordem')
    search_fields = ('nome', 'slug')
    prepopulated_fields = {'slug': ('nome',)}
    list_editable = ('ordem',)
    ordering = ('ordem', 'nome')

    def quantidade_produtos(self, obj):
        return obj.produtos.filter(status='ativo').count()
    quantidade_produtos.short_description = 'Produtos Ativos'


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'slug', 'categoria', 'status')
        }),
        ('Descrição', {
            'fields': ('resumo', 'descricao')
        }),
        ('Preço e Desconto', {
            'fields': ('preco', 'preco_original', 'percentual_desconto_display')
        }),
        ('Imagem', {
            'fields': ('imagem', 'imagem_preview')
        }),
        ('Destaque e Datas', {
            'fields': ('destaque', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )

    list_display = (
        'nome_truncado',
        'categoria',
        'preco',
        'status',
        'tem_desconto',
        'destaque',
    )
    list_filter = ('status', 'destaque', 'categoria', 'criado_em')
    search_fields = ('nome', 'descricao', 'slug')
    prepopulated_fields = {'slug': ('nome',)}
    readonly_fields = ('criado_em', 'atualizado_em', 'imagem_preview', 'percentual_desconto_display')
    ordering = ('-criado_em',)

    def nome_truncado(self, obj):
        nome = obj.nome[:50] + '...' if len(obj.nome) > 50 else obj.nome
        return nome
    nome_truncado.short_description = 'Produto'

    def percentual_desconto_display(self, obj):
        if obj.tem_desconto:
            return f'{obj.percentual_desconto}%'
        return '—'
    percentual_desconto_display.short_description = 'Percentual de Desconto'

    def imagem_preview(self, obj):
        if obj.imagem:
            return f'<img src="{obj.imagem.url}" style="max-width: 300px;" />'
        return 'Sem imagem'
    imagem_preview.short_description = 'Prévia da Imagem'


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    fields = ('produto', 'preco')
    readonly_fields = ('preco',)
    can_delete = True


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Cliente', {
            'fields': ('usuario', 'total')
        }),
        ('Status do Pedido', {
            'fields': ('status',)
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )

    list_display = ('pedido_id', 'usuario', 'total', 'status', 'data_pedido', 'itens_count')
    list_filter = ('status', 'criado_em')
    search_fields = ('usuario__username', 'usuario__email', 'id')
    readonly_fields = ('total', 'criado_em', 'atualizado_em')
    inlines = (ItemPedidoInline,)
    ordering = ('-criado_em',)

    def pedido_id(self, obj):
        return f'Pedido #{obj.id}'
    pedido_id.short_description = 'ID'

    def data_pedido(self, obj):
        return obj.criado_em.strftime('%d/%m/%Y %H:%M')
    data_pedido.short_description = 'Data'

    def itens_count(self, obj):
        return f'{obj.itens.count()} item(ns)'
    itens_count.short_description = 'Itens'


class ItemCarrinhoInline(admin.TabularInline):
    model = ItemCarrinho
    extra = 0
    fields = ('produto', 'quantidade')
    can_delete = True


@admin.register(Carrinho)
class CarrinhoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Cliente', {
            'fields': ('usuario', 'total', 'quantidade_itens_display')
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )

    list_display = ('usuario', 'total', 'quantidade_itens_display', 'data_atualizacao')
    list_filter = ('criado_em', 'atualizado_em')
    search_fields = ('usuario__username', 'usuario__email')
    readonly_fields = ('quantidade_itens_display', 'criado_em', 'atualizado_em')
    inlines = (ItemCarrinhoInline,)
    ordering = ('-atualizado_em',)
    can_delete = True

    def quantidade_itens_display(self, obj):
        return obj.quantidade_itens
    quantidade_itens_display.short_description = 'Itens'

    def data_atualizacao(self, obj):
        return obj.atualizado_em.strftime('%d/%m/%Y %H:%M')
    data_atualizacao.short_description = 'Atualizado em'

    def sem_itens(self, obj):
        if obj.quantidade_itens == 0:
            return format_html(
                '<span style="color: #D97706; font-weight: 600;">📦 Vazio</span>'
            )
        return '—'
    sem_itens.short_description = 'Info'
    list_display = ['usuario', 'quantidade_itens', 'total', 'atualizado_em']
    inlines      = [ItemCarrinhoInline]