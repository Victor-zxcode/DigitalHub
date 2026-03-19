from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produto, Categoria, Pedido, ItemPedido
from .forms import FormCadastro, FormLogin, FormContato
from django.db import models
from django.core.paginator import Paginator



def home(request):
    produtos = Produto.objects.filter(
        status='ativo',
        destaque=True
    ).order_by('-criado_em')[:8]

    categorias = Categoria.objects.filter(ativa=True)

    context = {
        'produtos': produtos,
        'categorias': categorias,
        'total_produtos': Produto.objects.filter(status='ativo').count(),
    }
    return render(request, 'home.html', context)


from django.core.paginator import Paginator


def produtos(request):
    lista = Produto.objects.filter(status='ativo').order_by('-criado_em')

    # Busca
    busca = request.GET.get('q', '').strip()
    if busca:
        lista = lista.filter(
            models.Q(nome__icontains=busca) |
            models.Q(descricao__icontains=busca) |
            models.Q(resumo__icontains=busca)
        )

    # Filtro por categoria
    categoria_slug = request.GET.get('categoria', '')
    categoria_ativa = None
    if categoria_slug:
        categoria_ativa = Categoria.objects.filter(slug=categoria_slug).first()
        if categoria_ativa:
            lista = lista.filter(categoria=categoria_ativa)

    # Paginação — 9 produtos por página
    paginator = Paginator(lista, 9)
    pagina    = request.GET.get('page', 1)
    produtos  = paginator.get_page(pagina)

    categorias = Categoria.objects.filter(ativa=True)

    return render(request, 'produtos.html', {
        'produtos':         produtos,
        'categorias':       categorias,
        'busca':            busca,
        'categoria_ativa':  categoria_ativa,
        'total_resultados': paginator.count,
    })


def categorias(request):
    lista = Categoria.objects.filter(ativa=True)
    return render(request, 'categorias.html', {'categorias': lista})


def categoria_detalhe(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug, ativa=True)
    lista = Produto.objects.filter(categoria=categoria, status='ativo')
    return render(request, 'categoria_detalhe.html', {
        'categoria': categoria,
        'produtos': lista,
    })


def ofertas(request):
    lista = Produto.objects.filter(
        status='ativo',
        preco_original__isnull=False
    ).order_by('-criado_em')
    return render(request, 'ofertas.html', {'produtos': lista})


def contato(request):
    form = FormContato(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # Em produção: enviar e-mail com django.core.mail.send_mail
            messages.success(request, 'Mensagem enviada com sucesso! Retornaremos em breve.')
            return redirect('contato')
        else:
            messages.error(request, 'Corrija os erros abaixo.')

    return render(request, 'contato.html', {'form': form})

def produto_detalhe(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id, status='ativo')
    relacionados = Produto.objects.filter(
        status='ativo',
        categoria=produto.categoria
    ).exclude(id=produto.id)[:4]
    return render(request, 'produto_detalhe.html', {
        'produto': produto,
        'relacionados': relacionados,
    })


def comprar_produto(request, produto_id):
    return render(request, 'comprar.html', {})


# ── Autenticação ────────────────────────────────────────────────

def cadastro(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = FormCadastro(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f'Bem-vindo, {usuario.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Corrija os erros abaixo.')

    return render(request, 'cadastro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = FormLogin(request, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            messages.success(request, f'Bem-vindo de volta, {usuario.username}!')
            # Redireciona para a página que o usuário tentou acessar
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('home')


@login_required
def minha_conta(request):
    return render(request, 'minha_conta.html', {'usuario': request.user})


@login_required
def comprar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id, status='ativo')

    # Verifica se o usuário já comprou esse produto
    ja_comprou = ItemPedido.objects.filter(
        pedido__usuario=request.user,
        pedido__status='pago',
        produto=produto
    ).exists()

    return render(request, 'checkout.html', {
        'produto': produto,
        'ja_comprou': ja_comprou,
    })


@login_required
def confirmar_compra(request, produto_id):
    if request.method != 'POST':
        return redirect('produto_detalhe', produto_id=produto_id)

    produto = get_object_or_404(Produto, id=produto_id, status='ativo')

    # Evita compra duplicada
    ja_comprou = ItemPedido.objects.filter(
        pedido__usuario=request.user,
        pedido__status='pago',
        produto=produto
    ).exists()

    if ja_comprou:
        messages.warning(request, 'Você já adquiriu este produto.')
        return redirect('minha_conta')

    # Cria o pedido
    pedido = Pedido.objects.create(
        usuario=request.user,
        status=Pedido.Status.PAGO,   # simulação: em produção viria do gateway
        total=produto.preco
    )
    ItemPedido.objects.create(
        pedido=pedido,
        produto=produto,
        preco=produto.preco
    )

    messages.success(request, f'Compra de "{produto.nome}" realizada com sucesso!')
    return redirect('pedido_confirmado', pedido_id=pedido.id)


@login_required
def pedido_confirmado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, 'pedido_confirmado.html', {'pedido': pedido})


@login_required
def minha_conta(request):
    pedidos = Pedido.objects.filter(
        usuario=request.user
    ).prefetch_related('itens__produto')
    return render(request, 'minha_conta.html', {
        'usuario': request.user,
        'pedidos': pedidos,
    })