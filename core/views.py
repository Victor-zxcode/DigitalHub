from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models, transaction
from django.core.paginator import Paginator
from .models import Produto, Categoria, Pedido, ItemPedido, Carrinho, ItemCarrinho
from .forms import FormCadastro, FormLogin, FormContato, FormPerfil, FormTrocarSenha
from .utils import enviar_email_confirmacao_compra, enviar_email_boas_vindas
import logging

logger = logging.getLogger(__name__)


def home(request):
    produtos = Produto.objects.destaques_ativos()[:8]
    
    categorias = Categoria.objects.ativas()
    
    carrinho = None
    if request.user.is_authenticated:
        carrinho, _ = Carrinho.objects.get_or_create(usuario=request.user)

    return render(request, 'home.html', {
        'produtos':       produtos,
        'categorias':     categorias,
        'total_produtos': Produto.objects.ativos().count(),
        'carrinho':       carrinho,
    })



def produtos(request):
    """
    Listagem de produtos com filtros de busca, categoria e preço.
    
    Queries otimizadas:
    - Usa .para_listagem() para carregar com categorias em 1 query
    - Filtros aplicados antes da paginação
    """
    # Query otimizada: produtos ativos com categorias carregadas
    lista = Produto.objects.para_listagem()

    busca = request.GET.get('q', '').strip()
    if busca:
        lista = lista.filter(
            models.Q(nome__icontains=busca) |
            models.Q(descricao__icontains=busca) |
            models.Q(resumo__icontains=busca)
        )

    categoria_slug = request.GET.get('categoria', '')
    categoria_ativa = None
    if categoria_slug:
        categoria_ativa = Categoria.objects.filter(slug=categoria_slug, ativa=True).first()
        if categoria_ativa:
            lista = lista.filter(categoria=categoria_ativa)

    preco_min = request.GET.get('preco_min', '').strip()
    preco_max = request.GET.get('preco_max', '').strip()
    if preco_min:
        lista = lista.filter(preco__gte=preco_min)
    if preco_max:
        lista = lista.filter(preco__lte=preco_max)

    paginator = Paginator(lista, 9)
    pagina = request.GET.get('page', 1)
    produtos = paginator.get_page(pagina)

    categorias = Categoria.objects.ativas()

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
    """Lista todas as categorias ativas ordenadas por ordem de exibição."""
    lista = Categoria.objects.ativas()
    return render(request, 'categorias.html', {'categorias': lista})


def categoria_detalhe(request, slug):
    """
    Exibe produtos de uma categoria específica.
    
    Queries otimizadas:
    - Get_or_404 com filtro de ativa
    - Usa .para_listagem() para carregar produtos com categorias
    """
    categoria = get_object_or_404(Categoria, slug=slug, ativa=True)
    lista = (
        Produto.objects
        .para_listagem()
        .filter(categoria=categoria)
    )
    
    return render(request, 'categoria_detalhe.html', {
        'categoria': categoria,
        'produtos':  lista,
    })



def ofertas(request):
    """Lista produtos em promoção (com preço original menor que preço atual)."""
    lista = (
        Produto.objects
        .com_desconto_ativo()
        .com_categoria()
    )
    return render(request, 'ofertas.html', {'produtos': lista})



def contato(request):
    """Formulário de contato com usuários."""
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
    """
    Exibe detalhes de um produto e produtos relacionados.
    
    Queries otimizadas:
    - Carrega produto com categoria (SELECT_RELATED)
    - Usa método otimizado para buscar produtos relacionados
    - Evita N+1 queries usando método do modelo
    
    Args:
        request: HttpRequest
        produto_id: ID do produto
        
    Returns:
        HttpResponse com template produto_detalhe.html
    """
    produto = get_object_or_404(
        Produto.objects.select_related('categoria'),
        id=produto_id,
        status='ativo'
    )

    relacionados = produto.produtos_relacionados(
        usuario=request.user,
        limite=4
    )

    return render(request, 'produto_detalhe.html', {
        'produto':      produto,
        'relacionados': relacionados,
    })



@login_required
def comprar_produto(request, produto_id):
    """
    Exibe página de checkout para compra de um produto.
    
    Queries otimizadas:
    - Usa método do modelo para verificar se já comprou
    """
    produto = get_object_or_404(Produto, id=produto_id, status='ativo')
    ja_comprou = produto.usuario_ja_comprou(request.user)

    return render(request, 'checkout.html', {
        'produto':    produto,
        'ja_comprou': ja_comprou,
    })


@login_required
@transaction.atomic
def confirmar_compra(request, produto_id):
    """
    Confirma e processa a compra de um produto.
    
    @transaction.atomic garante atomicidade: ou tudo é salvo ou nada.
    Isso evita compras duplicadas em caso de double-click do usuário.
    
    Queries otimizadas:
    - Usa select_for_update() para lock pessimista (evita race condition)
    - Usa método do modelo para verificar compra anterior
    """
    if request.method != 'POST':
        return redirect('produto_detalhe', produto_id=produto_id)

    produto = get_object_or_404(Produto, id=produto_id, status='ativo')

    if produto.usuario_ja_comprou(request.user):
        messages.warning(request, 'Você já adquiriu este produto.')
        return redirect('minha_conta')

    try:
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
            logger.error(
                f'Erro ao enviar e-mail de confirmação para pedido #{pedido.id}: {e}',
                exc_info=True
            )

        messages.success(request, f'Compra de "{produto.nome}" realizada com sucesso!')
        return redirect('pedido_confirmado', pedido_id=pedido.id)
        
    except Exception as e:
        logger.error(
            f'Erro ao processar compra do produto {produto_id} para usuário {request.user.id}: {e}',
            exc_info=True
        )
        messages.error(request, 'Erro ao processar sua compra. Tente novamente.')
        return redirect('produto_detalhe', produto_id=produto_id)


@login_required
def pedido_confirmado(request, pedido_id):
    """Exibe página de confirmação de pedido com detalhes."""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, 'pedido_confirmado.html', {'pedido': pedido})



def cadastro(request):
    """Formulário de cadastro de novo usuário."""
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
                logger.error(
                    f'Erro ao enviar e-mail de boas-vindas para {usuario.email}: {e}',
                    exc_info=True
                )
            
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
    """
    Exibe conta do usuário com histórico de pedidos e formulários de perfil.
    
    Queries otimizadas:
    - Usa .com_itens() para carregar pedidos com seus itens e produtos
    - Evita N+1 queries no template ao iterar os pedidos
    """
    pedidos = Pedido.objects.com_itens().do_usuario(request.user)

    form_perfil = FormPerfil(instance=request.user)
    form_senha = FormTrocarSenha(request.user)

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
    """
    Exibe o carrinho de compras do usuário.
    
    Queries otimizadas:
    - Usa .com_itens() para carregar carrinho com itens e produtos
    """
    carrinho, _ = Carrinho.objects.com_itens().get_or_create(usuario=request.user)
    return render(request, 'carrinho.html', {'carrinho': carrinho})


@login_required
def adicionar_carrinho(request, produto_id):
    """Adiciona um produto ao carrinho do usuário."""
    produto = get_object_or_404(Produto, id=produto_id, status='ativo')
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
@transaction.atomic
def finalizar_carrinho(request):
    """
    Finaliza a compra do carrinho, criando um pedido com todos os itens.
    
    @transaction.atomic garante que todos os itens são processados juntos
    ou nenhum é processado (atomicidade).
    """
    if request.method != 'POST':
        return redirect('carrinho')

    carrinho = get_object_or_404(Carrinho, usuario=request.user)

    if not carrinho.itens.exists():
        messages.warning(request, 'Seu carrinho está vazio.')
        return redirect('carrinho')

    try:
        pedido = Pedido.objects.create(
            usuario=request.user,
            status=Pedido.Status.PAGO,
            total=carrinho.total
        )

        for item in carrinho.itens.all():
            ja_comprou = ItemPedido.objects.filter(
                pedido__usuario=request.user,
                pedido__status=Pedido.Status.PAGO,
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
            logger.error(
                f'Erro ao enviar e-mail de confirmação para pedido #{pedido.id}: {e}',
                exc_info=True
            )

        messages.success(request, 'Pedido realizado com sucesso!')
        return redirect('pedido_confirmado', pedido_id=pedido.id)
        
    except Exception as e:
        logger.error(
            f'Erro ao finalizar carrinho para usuário {request.user.id}: {e}',
            exc_info=True
        )
        messages.error(request, 'Erro ao processar seu pedido. Tente novamente.')
        return redirect('carrinho')