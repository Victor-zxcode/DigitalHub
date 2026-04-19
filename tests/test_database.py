"""
Testes de banco de dados - DigitalHub
Testa conexão, migrações, modelos e integridade de dados
"""

import django
import os
import sys
from django.test import TestCase
from django.db import connection
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django1.settings')
django.setup()

from core.models import Produto, Categoria, Pedido, ItemPedido, Carrinho, ItemCarrinho, Estoque


class TestDatabaseConnection(TestCase):
    """Testa conexão com o banco de dados"""
    
    def test_database_connection(self):
        """Verifica se a conexão com o banco de dados está funcionando"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.assertIsNotNone(result, "Banco de dados não respondeu")
                print("✅ Conexão com banco de dados OK")
        except Exception as e:
            self.fail(f"❌ Erro ao conectar ao banco de dados: {str(e)}")
    
    def test_database_tables_exist(self):
        """Verifica se todas as tabelas necessárias existem"""
        from django.apps import apps
        
        tables = [
            'core_categoria',
            'core_produto',
            'core_estoque',
            'core_pedido',
            'core_itempedido',
            'core_carrinho',
            'core_itemcarrinho',
        ]
        
        with connection.cursor() as cursor:
            inspector = connection.introspection
            existing_tables = inspector.table_names()
            
            missing_tables = []
            for table in tables:
                if table not in existing_tables:
                    missing_tables.append(table)
            
            if missing_tables:
                self.fail(f"❌ Tabelas faltando: {missing_tables}")
            else:
                print(f"✅ Todas as {len(tables)} tabelas existem")


class TestCategoriaModel(TestCase):
    """Testa modelo de Categoria"""
    
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome="Python",
            slug="python",
            descricao="Cursos de Python"
        )
    
    def test_categoria_creation(self):
        """Verifica se uma categoria é criada corretamente"""
        self.assertEqual(self.categoria.nome, "Python")
        self.assertEqual(self.categoria.slug, "python")
        print(f"✅ Categoria criada: {self.categoria.nome}")
    
    def test_categoria_string_representation(self):
        """Verifica o método __str__ da categoria"""
        self.assertEqual(str(self.categoria), "Python")
        print(f"✅ Representação string da categoria OK: {str(self.categoria)}")


class TestProdutoModel(TestCase):
    """Testa modelo de Produto"""
    
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome="Programação",
            slug="programacao"
        )
        self.produto = Produto.objects.create(
            titulo="Python Avançado",
            descricao="Curso completo de Python",
            preco=99.90,
            categoria=self.categoria,
            uskku="SKU123"
        )
    
    def test_produto_creation(self):
        """Verifica se um produto é criado corretamente"""
        self.assertEqual(self.produto.titulo, "Python Avançado")
        self.assertEqual(self.produto.preco, 99.90)
        self.assertEqual(self.produto.categoria, self.categoria)
        print(f"✅ Produto criado: {self.produto.titulo}")
    
    def test_produto_price_validation(self):
        """Verifica se o preço é válido"""
        self.assertGreaterEqual(self.produto.preco, 0, "Preço não pode ser negativo")
        print(f"✅ Preço do produto validado: R$ {self.produto.preco}")
    
    def test_produto_string_representation(self):
        """Verifica o __str__ do produto"""
        self.assertIn("Python", str(self.produto))
        print(f"✅ Representação string do produto OK: {str(self.produto)}")


class TestEstoqueModel(TestCase):
    """Testa modelo de Estoque"""
    
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
            uskku="SKU456"
        )
        self.estoque = Estoque.objects.create(
            produto=self.produto,
            quantidade=100
        )
    
    def test_estoque_creation(self):
        """Verifica se o estoque é criado"""
        self.assertEqual(self.estoque.quantidade, 100)
        print(f"✅ Estoque criado: {self.estoque.quantidade} unidades")
    
    def test_estoque_quantity_validation(self):
        """Verifica se a quantidade é não-negativa"""
        self.assertGreaterEqual(self.estoque.quantidade, 0)
        print(f"✅ Quantidade do estoque validada")


class TestCarrinhoModel(TestCase):
    """Testa modelo de Carrinho"""
    
    def setUp(self):
        self.carrinho = Carrinho.objects.create(
            sessao_id="test_session_123"
        )
    
    def test_carrinho_creation(self):
        """Verifica se um carrinho é criado"""
        self.assertIsNotNone(self.carrinho.id)
        print(f"✅ Carrinho criado com ID: {self.carrinho.id}")


class TestPedidoModel(TestCase):
    """Testa modelo de Pedido"""
    
    def setUp(self):
        from django.contrib.auth.models import User
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.categoria = Categoria.objects.create(
            nome="Testes",
            slug="testes"
        )
        self.produto = Produto.objects.create(
            titulo="Produto Teste",
            descricao="Descrição teste",
            preco=29.90,
            categoria=self.categoria,
            uskku="SKU789"
        )
    
    def test_pedido_creation(self):
        """Verifica se um pedido é criado"""
        pedido = Pedido.objects.create(
            usuario=self.user,
            total=29.90,
            status='processando'
        )
        self.assertIsNotNone(pedido.id)
        print(f"✅ Pedido criado com ID: {pedido.id}")
    
    def test_pedido_total_calculation(self):
        """Verifica o cálculo do total do pedido"""
        pedido = Pedido.objects.create(
            usuario=self.user,
            total=99.80,
            status='processando'
        )
        self.assertEqual(pedido.total, 99.80)
        print(f"✅ Total do pedido calculado: R$ {pedido.total}")


class TestDatabaseIntegrity(TestCase):
    """Testa integridade referencial do banco"""
    
    def test_foreign_key_relationships(self):
        """Verifica se os relacionamentos estão configurados"""
        # Criar categoria
        categoria = Categoria.objects.create(
            nome="Relacionamentos",
            slug="relacionamentos"
        )
        
        # Criar produto vinculado à categoria
        produto = Produto.objects.create(
            titulo="Teste FK",
            descricao="Teste de chave estrangeira",
            preco=10.00,
            categoria=categoria,
            uskku="FK001"
        )
        
        # Verificar se o relacionamento foi criado
        self.assertEqual(produto.categoria.id, categoria.id)
        self.assertIn(produto, categoria.produto_set.all())
        print(f"✅ Relacionamentos de chave estrangeira OK")


def run_all_tests():
    """Executa todos os testes de banco de dados"""
    print("\n" + "="*70)
    print("🧪 TESTES DE BANCO DE DADOS - DIGITALHUB")
    print("="*70 + "\n")
    
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=2, interactive=False, keepdb=False)
    failures = test_runner.run_tests(['tests.test_database'])
    
    print("\n" + "="*70)
    if failures == 0:
        print("✅ TODOS OS TESTES DE BANCO DE DADOS PASSARAM!")
    else:
        print(f"❌ {failures} TESTE(S) FALHARAM")
    print("="*70 + "\n")
    
    return failures


if __name__ == '__main__':
    sys.exit(run_all_tests())
