from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'


class Categoria(models.Model):
    nome    = models.CharField(max_length=100, unique=True)
    slug    = models.SlugField(max_length=120, unique=True, blank=True)
    icone   = models.CharField(max_length=10, blank=True)   # emoji: 🎓 📚 ⚙️
    ativa   = models.BooleanField(default=True)
    ordem   = models.PositiveIntegerField(default=0)        # controla a ordem de exibição

    class Meta:
        ordering = ['ordem', 'nome']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('categoria_detalhe', kwargs={'slug': self.slug})


class Produto(models.Model):

    class Status(models.TextChoices):
        ATIVO    = 'ativo',    'Ativo'
        INATIVO  = 'inativo',  'Inativo'
        RASCUNHO = 'rascunho', 'Rascunho'

    nome           = models.CharField(max_length=200)
    slug           = models.SlugField(max_length=220, unique=True, blank=True)
    descricao      = models.TextField()
    resumo         = models.CharField(max_length=300, blank=True)
    preco          = models.DecimalField(max_digits=8, decimal_places=2)
    preco_original = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    imagem         = models.ImageField(upload_to='produtos/', blank=True, null=True)
    status         = models.CharField(max_length=20, choices=Status.choices, default=Status.RASCUNHO)
    destaque       = models.BooleanField(default=False)

    # ← novo: vínculo com Categoria
    categoria      = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,   # se a categoria for deletada, o produto não some
        null=True,
        blank=True,
        related_name='produtos'
    )

    criado_em      = models.DateTimeField(auto_now_add=True)
    atualizado_em  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('produto_detalhe', kwargs={'produto_id': self.id})

    @property
    def tem_desconto(self):
        return self.preco_original and self.preco_original > self.preco

    @property
    def percentual_desconto(self):
        if self.tem_desconto:
            diff = self.preco_original - self.preco
            return int((diff / self.preco_original) * 100)
        return 0


class Pedido(models.Model):

    class Status(models.TextChoices):
        PENDENTE   = 'pendente',   'Pendente'
        PAGO       = 'pago',       'Pago'
        CANCELADO  = 'cancelado',  'Cancelado'

    usuario    = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    status     = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE
    )
    total      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    criado_em  = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f'Pedido #{self.id} — {self.usuario.username}'

    def calcular_total(self):
        self.total = sum(item.preco for item in self.itens.all())
        self.save()


class ItemPedido(models.Model):
    pedido   = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    produto  = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,  # não deixa deletar produto com pedido
        related_name='itens_pedido'
    )
    # Guardamos o preço no momento da compra
    # (o preço do produto pode mudar depois)
    preco    = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        return f'{self.produto.nome} — Pedido #{self.pedido.id}'