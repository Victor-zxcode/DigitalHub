from django.urls import path
from core import views

urlpatterns = [
    path('',                                      views.home,              name='home'),
    path('produtos/',                             views.produtos,          name='produtos'),
    path('categorias/',                           views.categorias,        name='categorias'),
    path('categorias/<slug:slug>/',               views.categoria_detalhe, name='categoria_detalhe'),
    path('ofertas/',                              views.ofertas,           name='ofertas'),
    path('contato/',                              views.contato,           name='contato'),
    path('login/',                                views.login_view,        name='login'),
    path('cadastro/',                             views.cadastro,          name='cadastro'),
    path('logout/',                               views.logout_view,       name='logout'),
    path('minha-conta/',                          views.minha_conta,       name='minha_conta'),
    path('produto/<int:produto_id>/',             views.produto_detalhe,   name='produto_detalhe'),
    path('produto/<int:produto_id>/comprar/',     views.comprar_produto,   name='comprar_produto'),
    path('produto/<int:produto_id>/confirmar/',   views.confirmar_compra,  name='confirmar_compra'),
    path('pedido/<int:pedido_id>/confirmado/',    views.pedido_confirmado, name='pedido_confirmado'),
    path('como-funciona/', views.como_funciona, name='como_funciona'),
]