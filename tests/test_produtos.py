"""
Testes de produtos - DigitalHub
Testa criação, listagem, filtros e detalhes de produtos
"""

import django
import os
from django.test import TestCase

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django1.settings')
django.setup()

from core.models import Categoria, Produto, Estoque


class TestProdutoCreation(TestCase):
    """Testa criação de produtos"""
    
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome="Programação",
            slug="programacao",
            descricao="Cursos de programação"
        )
    
    def test_create_simple_produto(self):
        """Testa criação de um produto simples"""
        produto = Produto.objects.create(
            titulo="Python Completo",
            descricao="Aprenda Python do zero",
            preco=99.90,
            categoria=self.categoria,
            uskku="PY001"
        )
        self.assertEqual(produto.titulo, "Python Completo")
        self.assertEqual(produto.preco, 99.90)
        print(f"✅ Produto criado: {produto.titulo}")
    
    def test_produto_with_all_fields(self):
        """Testa criação de produto com todos os campos"""
        produto = Produto.objects.create(
            titulo="JavaScript Avançado",
            descricao="Dominar JavaScript moderno",
            preco=149.90,
            category=self.categoria,
            uskku="JS001",
            imagem=None
        )
        self.assertIsNotNone(produto.id)
        self.assertEqual(produto.categoria.id, self.categoria.id)
        print(f"✅ Produto completo criado: {produto.titulo}")
    
    def test_multiple_products_same_category(self):
        """Testa criação de múltiplos produtos em mesma categoria"""
        produtos = []
        for i in range(3):
            produto = Produto.objects.create(
                titulo=f"Curso {i+1}",
                descricao=f"Descrição do curso {i+1}",
                preco=50 + i * 10,
                categoria=self.categoria,
                uskku=f"CRS{i+1}"
            )
            produtos.append(produto)
        
        self.assertEqual(len(produtos), 3)
        self.assertEqual(self.categoria.produto_set.count(), 3)
        print(f"✅ {len(produtos)} produtos criados na mesma categoria")


class TestProdutoFiltering(TestCase):
    """Testa filtragem de produtos"""
    
    def setUp(self):
        self.categoria1 = Categoria.objects.create(
            nome="Python",
            slug="python"
        )
        self.categoria2 = Categoria.objects.create(
            nome="JavaScript",
            slug="javascript"
        )
        
        # Criar produtos
        self.p1 = Produto.objects.create(
            titulo="Python Básico",
            descricao="Iniciante",
            preco=49.90,
            categoria=self.categoria1,
            uskku="PYB"
        )
        self.p2 = Produto.objects.create(
            titulo="Python Avançado",
            descricao="Avançado",
            preco=149.90,
            categoria=self.categoria1,
            uskku="PYA"
        )
        self.p3 = Produto.objects.create(
            titulo="JavaScript Básico",
            descricao="Iniciante",
            preco=59.90,
            categoria=self.categoria2,
            uskku="JSB"
        )
    
    def test_filter_by_category(self):
        """Testa filtragem por categoria"""
        python_products = Produto.objects.filter(categoria=self.categoria1)
        self.assertEqual(python_products.count(), 2)
        print(f"✅ Filtro por categoria encontrou 2 produtos")
    
    def test_filter_by_price(self):
        """Testa filtragem por faixa de preço"""
        cheap_products = Produto.objects.filter(preco__lt=100)
        self.assertEqual(cheap_products.count(), 2)
        print(f"✅ Filtro por preço encontrou {cheap_products.count()} produtos")
    
    def test_filter_by_title_search(self):
        """Testa busca por título"""
        python_products = Produto.objects.filter(titulo__icontains="Python")
        self.assertEqual(python_products.count(), 2)
        print(f"✅ Busca por título encontrou {python_products.count()} produtos")
    
    def test_combined_filters(self):
        """Testa filtros combinados"""
        results = Produto.objects.filter(
            categoria=self.categoria1,
            preco__gt=100
        )
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().titulo, "Python Avançado")
        print(f"✅ Filtros combinados funcionam corretamente")


class TestProdutoEstoque(TestCase):
    """Testa gestão de estoque de produtos"""
    
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome="E-books",
            slug="ebooks"
        )
        self.produto = Produto.objects.create(
            titulo="E-book Python",
            descricao="E-book completo",
            preco=49.90,
            categoria=self.categoria,
            uskku="EBK001"
        )
    
    def test_estoque_creation(self):
        """Testa criação de estoque"""
        estoque = Estoque.objects.create(
            produto=self.produto,
            quantidade=100
        )
        self.assertEqual(estoque.quantidade, 100)
        print(f"✅ Estoque criado: {estoque.quantidade} unidades")
    
    def test_estoque_quantity_update(self):
        """Testa atualização de quantidade de estoque"""
        estoque = Estoque.objects.create(
            produto=self.produto,
            quantidade=50
        )
        estoque.quantidade = 30
        estoque.save()
        
        estoque_updated = Estoque.objects.get(id=estoque.id)
        self.assertEqual(estoque_updated.quantidade, 30)
        print(f"✅ Estoque atualizado para {estoque_updated.quantidade}")


class TestProdutoValidation(TestCase):
    """Testa validação de produtos"""
    
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome="Validação",
            slug="validacao"
        )
    
    def test_product_price_cannot_be_negative(self):
        """Testa que preço negativo é rejeitado"""
        with self.assertRaises(Exception):
            produto = Produto.objects.create(
                titulo="Produto Inválido",
                descricao="Test",
                preco=-10.00,
                categoria=self.categoria,
                uskku="INV"
            )
            if hasattr(produto, 'full_clean'):
                produto.full_clean()
        print(f"✅ Proteção contra preço negativo funciona")
    
    def test_product_title_required(self):
        """Testa que título é obrigatório"""
        with self.assertRaises(Exception):
            Produto.objects.create(
                titulo="",
                descricao="Sem título",
                preco=10.00,
                categoria=self.categoria,
                uskku="NOTITLE"
            )
        print(f"✅ Título obrigatório validado")


class TestProdutoOrdering(TestCase):
    """Testa ordenação de produtos"""
    
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome="Testes",
            slug="testes"
        )
        
        # Criar produtos com preços variados
        precos = [99.90, 29.90, 149.90, 49.90]
        for i, preco in enumerate(precos):
            Produto.objects.create(
                titulo=f"Produto {i+1}",
                descricao="Teste",
                preco=preco,
                categoria=self.categoria,
                uskku=f"ORD{i+1}"
            )
    
    def test_order_by_price_ascending(self):
        """Testa ordenação por preço crescente"""
        produtos = Produto.objects.all().order_by('preco')
        precos = [p.preco for p in produtos]
        self.assertEqual(precos, sorted(precos))
        print(f"✅ Produtos ordenados por preço crescente")
    
    def test_order_by_price_descending(self):
        """Testa ordenação por preço decrescente"""
        produtos = Produto.objects.all().order_by('-preco')
        first_preco = produtos.first().preco
        last_preco = produtos.last().preco
        self.assertGreater(first_preco, last_preco)
        print(f"✅ Produtos ordenados por preço decrescente")


def run_all_tests():
    """Executa todos os testes de produtos"""
    print("\n" + "="*70)
    print("📦 TESTES DE PRODUTOS - DIGITALHUB")
    print("="*70 + "\n")
    
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=2, interactive=False, keepdb=False)
    failures = test_runner.run_tests(['tests.test_produtos'])
    
    print("\n" + "="*70)
    if failures == 0:
        print("✅ TODOS OS TESTES DE PRODUTOS PASSARAM!")
    else:
        print(f"❌ {failures} TESTE(S) FALHARAM")
    print("="*70 + "\n")
    
    return failures


if __name__ == '__main__':
    import sys
    sys.exit(run_all_tests())
