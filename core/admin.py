from django.contrib import admin
from .models import Produtos, Clientes, Pedidos, Usuario

# Register your models here.

admin.site.register(Produtos)
admin.site.register(Clientes)
admin.site.register(Pedidos)
admin.site.register(Usuario)
