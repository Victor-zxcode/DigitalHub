from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Produtos(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(max_length=500)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.IntegerField()

    def __str__(self):
        return self.nome


class Clientes(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Pedidos(models.Model):
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produtos, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    data_pedido = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido de {self.cliente.nome} - {self.produto.nome}"
    

class Usuario(AbstractUser):
    telefone = models.CharField(max_length=20, blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True)
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)

    def __str__(self):
        return self.username

    