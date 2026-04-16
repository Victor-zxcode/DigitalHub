from django.db import models


class CategoriaQuerySet(models.QuerySet):
    def ativas(self):
        return self.filter(ativa=True).order_by('ordem', 'nome')


class CategoriaManager(models.Manager):
    def get_queryset(self):
        return CategoriaQuerySet(self.model, using=self._db)

    def ativas(self):
        return self.get_queryset().ativas()


class ProdutoQuerySet(models.QuerySet):
    def ativos(self):
        return self.filter(status='ativo')

    def com_categoria(self):
        return self.select_related('categoria')

    def destaques(self):
        return self.filter(destaque=True)

    def com_desconto(self):
        return self.exclude(preco_original__isnull=True)

    def ordenado_recente(self):
        return self.order_by('-criado_em')

    def para_listagem(self):
        return self.com_categoria().ordenado_recente()


class ProdutoManager(models.Manager):
    def get_queryset(self):
        return ProdutoQuerySet(self.model, using=self._db)

    def ativos(self):
        return self.get_queryset().ativos()

    def destaques_ativos(self):
        return self.get_queryset().ativos().destaques().ordenado_recente()

    def com_desconto_ativo(self):
        return self.get_queryset().ativos().com_desconto()

    def para_listagem(self):
        return self.get_queryset().para_listagem()


class PedidoQuerySet(models.QuerySet):
    def com_itens(self):
        return self.prefetch_related('itens__produto')

    def do_usuario(self, usuario):
        return self.filter(usuario=usuario)


class PedidoManager(models.Manager):
    def get_queryset(self):
        return PedidoQuerySet(self.model, using=self._db)

    def com_itens(self):
        return self.get_queryset().com_itens()

    def do_usuario(self, usuario):
        return self.get_queryset().do_usuario(usuario).com_itens()


class CarrinhoQuerySet(models.QuerySet):
    def com_itens(self):
        return self.prefetch_related('itens__produto__categoria')


class CarrinhoManager(models.Manager):
    def get_queryset(self):
        return CarrinhoQuerySet(self.model, using=self._db)

    def com_itens(self):
        return self.get_queryset().com_itens()
