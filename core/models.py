from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Produtos(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(max_length=500)
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return self.nome

class Estoques(models.Model):
    produto = models.OneToOneField(Produtos, on_delete=models.CASCADE, related_name="estoque")
    quantidade = models.IntegerField()

    class Meta:
        verbose_name = 'Estoque'
        verbose_name_plural = 'Estoques'

    def __str__(self):
        return f"Estoque de {self.produto.nome}: {self.quantidade}"




class Clientes(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.nome


class Pedidos(models.Model):
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produtos, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    data_pedido = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"Pedido de {self.cliente.nome} - {self.produto.nome}"
    

class Usuario(AbstractUser):
    telefone = models.CharField(max_length=20, blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True)
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.username


