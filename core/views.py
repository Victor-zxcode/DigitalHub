from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.core.paginator import Paginator
from .models import Produto, Categoria, Pedido, ItemPedido, Carrinho, ItemCarrinho
from .forms import FormCadastro, FormLogin, FormContato, FormPerfil, FormTrocarSenha
from .utils import enviar_email_confirmacao_compra, enviar_email_boas_vindas



def home(request):
    produtos = Produto.objects.filter(status='ativo', destaque=True).order_by('-criado_em')[:8]
    categorias = Categoria.objects.filter(ativa=True)
    carrinho = None
    if request.user.is_authenticated:
        carrinho, _ = Carrinho.objects.get_or_create(usuario=request.user)

    return render(request, 'home.html', {
        'produtos':       produtos,
        'categorias':     categorias,
        'total_produtos': Produto.objects.filter(status='ativo').count(),
        'carrinho':       carrinho,
    })



def produtos(request):
    lista = Produto.objects.filter(status='ativo').order_by('-criado_em')

    busca = request.GET.get('q', '').strip()
    if busca:
        lista = lista.filter(
            models.Q(nome__icontains=busca) or
            models.Q(descricao__icontains=busca) or
            models.Q(resumo__icontains=busca)
        )

    categoria_slug = request.GET.get('categoria', '')
    categoria_ativa = None
    if categoria_slug:
        categoria_ativa = Categoria.objects.filter(slug=categoria_slug).first()
        if categoria_ativa:
            lista = lista.filter(categoria=categoria_ativa)

    preco_min = request.GET.get('preco_min', '').strip()
    preco_max = request.GET.get('preco_max', '').strip()
    if preco_min:
        lista = lista.filter(preco__gte=preco_min)
    if preco_max:
        lista = lista.filter(preco__lte=preco_max)

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
        'preco_min':        preco_min,
        'preco_max':        preco_max,
    })


def categorias(request):
    lista = Categoria.objects.filter(ativa=True)
    return render(request, 'categorias.html', {'categorias': lista})



def categoria_detalhe(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug, ativa=True)
    lista = Produto.objects.filter(categoria=categoria, status='ativo')
    return render(request, 'categoria_detalhe.html', {
        'categoria': categoria,
        'produtos':  lista,
    })



def ofertas(request):
    lista = Produto.objects.filter(status='ativo', preco_original__isnull=False).order_by('-criado_em')
    return render(request, 'ofertas.html', {'produtos': lista})



def contato(request):
    form = FormContato(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            messages.success(request, 'Mensagem enviada com sucesso! Retornaremos em breve.')
            return redirect('contato')
        else:
            messages.error(request, 'Corrija os erros abaixo.')
    return render(request, 'contato.html', {'form': form})



def como_funciona(request):
    return render(request, 'como_funciona.html', {})



def produto_detalhe(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id, status='ativo')

    ja_comprados = []
    if request.user.is_authenticated:
        ja_comprados = ItemPedido.objects.filter(
            pedido__usuario=request.user,
            pedido__status='pago'
        ).values_list('produto_id', flat=True)

    relacionados = Produto.objects.filter(
        status='ativo',
        categoria=produto.categoria
    ).exclude(
        id=produto.id
    ).exclude(
        id__in=ja_comprados
    ).order_by('-destaque', 'preco_original', '-criado_em')[:4]

    if not relacionados.exists():
        relacionados = Produto.objects.filter(
            status='ativo'
        ).exclude(
            id=produto.id
        ).exclude(
            id__in=ja_comprados
        ).order_by('-destaque', '-criado_em')[:4]

    return render(request, 'produto_detalhe.html', {
        'produto':      produto,
        'relacionados': relacionados,
    })



@login_required
def comprar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id, status='ativo')

    ja_comprou = ItemPedido.objects.filter(
        pedido__usuario=request.user,
        pedido__status='pago',
        produto=produto
    ).exists()

    return render(request, 'checkout.html', {
        'produto':    produto,
        'ja_comprou': ja_comprou,
    })


@login_required
def confirmar_compra(request, produto_id):
    if request.method != 'POST':
        return redirect('produto_detalhe', produto_id=produto_id)

    produto = get_object_or_404(Produto, id=produto_id, status='ativo')

    ja_comprou = ItemPedido.objects.filter(
        pedido__usuario=request.user,
        pedido__status='pago',
        produto=produto
    ).exists()

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

    try:
        enviar_email_confirmacao_compra(pedido)
    except Exception as e:
        print(f'Erro ao enviar e-mail: {e}')

    messages.success(request, f'Compra de "{produto.nome}" realizada com sucesso!')
    return redirect('pedido_confirmado', pedido_id=pedido.id)


@login_required
def pedido_confirmado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, 'pedido_confirmado.html', {'pedido': pedido})



def cadastro(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = FormCadastro(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            try:
                enviar_email_boas_vindas(usuario)
            except Exception as e:
                print(f'Erro ao enviar e-mail: {e}')
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
    pedidos     = Pedido.objects.filter(
        usuario=request.user
    ).prefetch_related('itens__produto')

    form_perfil = FormPerfil(instance=request.user)
    form_senha  = FormTrocarSenha(request.user)

    if request.method == 'POST':

        if 'salvar_perfil' in request.POST:
            form_perfil = FormPerfil(request.POST, instance=request.user)
            if form_perfil.is_valid():
                form_perfil.save()
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('minha_conta')
            else:
                messages.error(request, 'Corrija os erros abaixo.')

        elif 'trocar_senha' in request.POST:
            form_senha = FormTrocarSenha(request.user, request.POST)
            if form_senha.is_valid():
                user = form_senha.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('minha_conta')
            else:
                messages.error(request, 'Corrija os erros abaixo.')

    return render(request, 'minha_conta.html', {
        'pedidos':     pedidos,
        'form_perfil': form_perfil,
        'form_senha':  form_senha,
        'usuario':     request.user,
    })



@login_required
def carrinho(request):
    carrinho, _ = Carrinho.objects.get_or_create(usuario=request.user)
    return render(request, 'carrinho.html', {'carrinho': carrinho})


@login_required
def adicionar_carrinho(request, produto_id):
    produto  = get_object_or_404(Produto, id=produto_id, status='ativo')
    carrinho, _ = Carrinho.objects.get_or_create(usuario=request.user)

    item, criado = ItemCarrinho.objects.get_or_create(
        carrinho=carrinho,
        produto=produto
    )

    if criado:
        messages.success(request, f'"{produto.nome}" adicionado ao carrinho.')
    else:
        messages.info(request, f'"{produto.nome}" já está no seu carrinho.')

    return redirect(request.META.get('HTTP_REFERER', 'carrinho'))


@login_required
def remover_carrinho(request, item_id):
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho__usuario=request.user)
    nome = item.produto.nome
    item.delete()
    messages.success(request, f'"{nome}" removido do carrinho.')
    return redirect('carrinho')


@login_required
def finalizar_carrinho(request):
    if request.method != 'POST':
        return redirect('carrinho')

    carrinho = get_object_or_404(Carrinho, usuario=request.user)

    if not carrinho.itens.exists():
        messages.warning(request, 'Seu carrinho está vazio.')
        return redirect('carrinho')

    pedido = Pedido.objects.create(
        usuario=request.user,
        status=Pedido.Status.PAGO,
        total=carrinho.total
    )

    for item in carrinho.itens.all():
        ja_comprou = ItemPedido.objects.filter(
            pedido__usuario=request.user,
            pedido__status='pago',
            produto=item.produto
        ).exists()

        if not ja_comprou:
            ItemPedido.objects.create(
                pedido=pedido,
                produto=item.produto,
                preco=item.produto.preco
            )

    carrinho.itens.all().delete()

    try:
        enviar_email_confirmacao_compra(pedido)
    except Exception as e:
        print(f'Erro ao enviar e-mail: {e}')

    messages.success(request, 'Pedido realizado com sucesso!')
    return redirect('pedido_confirmado', pedido_id=pedido.id)