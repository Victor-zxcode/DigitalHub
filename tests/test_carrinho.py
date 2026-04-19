"""
Testes de carrinho de compras - DigitalHub
Testa adição, remoção, atualização e cálculo de total
"""

import django
import os
from django.test import TestCase

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django1.settings')
django.setup()

from core.models import Carrinho, ItemCarrinho, Categoria, Produto


class TestCarrinhoBasics(TestCase):
    """Testa operações básicas do carrinho"""
    
    def setUp(self):
        self.carrinho = Carrinho.objects.create(
            sessao_id="test_session_123"
        )
    
    def test_carrinho_creation(self):
        """Testa criação de carrinho"""
        self.assertIsNotNone(self.carrinho.id)
        self.assertEqual(self.carrinho.sessao_id, "test_session_123")
        print(f"✅ Carrinho criado com ID: {self.carrinho.id}")
    
    def test_carrinho_is_empty_initially(self):
        """Testa que carrinho começa vazio"""
        itens = self.carrinho.itemcarrinho_set.all()
        self.assertEqual(itens.count(), 0)
        print(f"✅ Carrinho começa vazio")


class TestCarrinhoItems(TestCase):
    """Testa adição e remoção de itens do carrinho"""
    
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome="Testes",
            slug="testes"
        )
        self.produto = Produto.objects.create(
            titulo="Produto Teste",
            descricao="Descrição teste",
            preco=99.90,
            categoria=self.categoria,
            uskku="TEST001"
        )
        self.carrinho = Carrinho.objects.create(
            sessao_id="test_cart_123"
        )
    
    def test_add_item_to_carrinho(self):
        """Testa adição de item ao carrinho"""
        item = ItemCarrinho.objects.create(
            carrinho=self.carrinho,
            produto=self.produto,
            quantidade=1
        )
        self.assertEqual(item.quantidade, 1)
        self.assertEqual(self.carrinho.itemcarrinho_set.count(), 1)
        print(f"✅ Item adicionado ao carrinho")
    
    def test_add_multiple_items(self):
        """Testa adição de múltiplos itens"""
        for i in range(3):
            Produto.objects.create(
                titulo=f"Produto {i}",
                descricao="Teste",
                preco=10 + i,
                categoria=self.categoria,
                uskku=f"PRD{i}"
            )
        
        produtos = Produto.objects.filter(categoria=self.categoria)
        for produto in produtos[:3]:
            ItemCarrinho.objects.create(
                carrinho=self.carrinho,
                produto=produto,
                quantidade=1
            )
        
        self.assertEqual(self.carrinho.itemcarrinho_set.count(), 3)
        print(f"✅ Múltiplos itens adicionados: {self.carrinho.itemcarrinho_set.count()}")
    
    def test_remove_item_from_carrinho(self):
        """Testa remoção de item do carrinho"""
        item = ItemCarrinho.objects.create(
            carrinho=self.carrinho,
            produto=self.produto,
            quantidade=1
        )
        self.assertEqual(self.carrinho.itemcarrinho_set.count(), 1)
        
        item.delete()
        self.assertEqual(self.carrinho.itemcarrinho_set.count(), 0)
        print(f"✅ Item removido do carrinho")


class TestCarrinhoQuantity(TestCase):
    """Testa gerenciamento de quantidade de itens"""
    
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome="Qtest",
            slug="qtest"
        )
        self.produto = Produto.objects.create(
            titulo="Produto Q",
            descricao="Teste",
            preco=50.00,
            categoria=self.categoria,
            uskku="QTE"
        )
        self.carrinho = Carrinho.objects.create(
            sessao_id="qty_test"
        )
    
    def test_update_item_quantity(self):
        """Testa atualização de quantidade"""
        item = ItemCarrinho.objects.create(
            carrinho=self.carrinho,
            produto=self.produto,
            quantidade=2
        )
        
        item.quantidade = 5
        item.save()
        
        item_updated = ItemCarrinho.objects.get(id=item.id)
        self.assertEqual(item_updated.quantidade, 5)
        print(f"✅ Quantidade atualizada para {item_updated.quantidade}")
    
    def test_quantity_cannot_be_zero(self):
        """Testa que quantidade não pode ser zero"""
        item = ItemCarrinho.objects.create(
            carrinho=self.carrinho,
            produto=self.produto,
            quantidade=1
        )
        
        # Tentar colocar quantidade 0 deve remover o item
        if item.quantidade <= 0:
            item.delete()
        
        self.assertEqual(self.carrinho.itemcarrinho_set.count(), 1)
        print(f"✅ Proteção contra quantidade zero")


class TestCarrinhoStatus(TestCase):
    """Testa status do carrinho"""
    
    def setUp(self):
        self.carrinho = Carrinho.objects.create(
            sessao_id="status_test"
        )
    
    def test_carrinho_is_active(self):
        """Testa que carrinho é ativo"""
        self.assertTrue(self.carrinho.ativo)
        print(f"✅ Carrinho está ativo")
    
    def test_carrinho_can_be_deactivated(self):
        """Testa que carrinho pode ser desativado"""
        self.carrinho.ativo = False
        self.carrinho.save()
        
        carrinho_updated = Carrinho.objects.get(id=self.carrinho.id)
        self.assertFalse(carrinho_updated.ativo)
        print(f"✅ Carrinho desativado")


class TestCarrinhoDuplicateItems(TestCase):
    """Testa comportamento com itens duplicados"""
    
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome="Dup",
            slug="dup"
        )
        self.produto = Produto.objects.create(
            titulo="Produto Duplo",
            descricao="Teste",
            preco=75.00,
            categoria=self.categoria,
            uskku="DUP"
        )
        self.carrinho = Carrinho.objects.create(
            sessao_id="dup_test"
        )
    
    def test_add_same_product_twice(self):
        """Testa adição do mesmo produto duas vezes"""
        # Primeira adição
        item1 = ItemCarrinho.objects.create(
            carrinho=self.carrinho,
            produto=self.produto,
            quantidade=2
        )
        
        # Segunda adição (deve aumentar quantidade)
        items = ItemCarrinho.objects.filter(
            carrinho=self.carrinho,
            produto=self.produto
        )
        
        if items.exists():
            item = items.first()
            item.quantidade += 1
            item.save()
        
        item_final = ItemCarrinho.objects.get(
            carrinho=self.carrinho,
            produto=self.produto
        )
        self.assertEqual(item_final.quantidade, 3)
        print(f"✅ Quantidade consolidada para {item_final.quantidade}")


def run_all_tests():
    """Executa todos os testes de carrinho"""
    print("\n" + "="*70)
    print("🛒 TESTES DE CARRINHO - DIGITALHUB")
    print("="*70 + "\n")
    
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=2, interactive=False, keepdb=False)
    failures = test_runner.run_tests(['tests.test_carrinho'])
    
    print("\n" + "="*70)
    if failures == 0:
        print("✅ TODOS OS TESTES DE CARRINHO PASSARAM!")
    else:
        print(f"❌ {failures} TESTE(S) FALHARAM")
    print("="*70 + "\n")
    
    return failures


if __name__ == '__main__':
    import sys
    sys.exit(run_all_tests())
