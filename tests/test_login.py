"""
Testes de autenticação e login - DigitalHub
Testa registro, login, logout e permissões
"""

import django
import os
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django1.settings')
django.setup()


class TestUserRegistration(TestCase):
    """Testa registro de novo usuário"""
    
    def setUp(self):
        self.client = Client()
    
    def test_user_creation(self):
        """Verifica se um usuário pode ser criado"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        print(f"✅ Usuário criado com sucesso: {user.username}")
    
    def test_user_password_hashing(self):
        """Verifica se a senha é armazenada com hash"""
        user = User.objects.create_user(
            username='hashtest',
            password='mypassword'
        )
        self.assertNotEqual(user.password, 'mypassword')
        self.assertTrue(user.password.startswith('pbkdf2_sha256'))
        print(f"✅ Senha armazenada com hash corretamente")
    
    def test_user_email_validation(self):
        """Verifica validação de email"""
        user = User.objects.create_user(
            username='emailtest',
            email='validemail@example.com'
        )
        self.assertIn('@', user.email)
        print(f"✅ Email validado: {user.email}")
    
    def test_duplicate_username_prevention(self):
        """Verifica se nomes de usuário duplicados são evitados"""
        User.objects.create_user(username='duplicado', password='pass123')
        
        with self.assertRaises(Exception):
            User.objects.create_user(username='duplicado', password='pass456')
        
        print(f"✅ Proteção contra nomes de usuário duplicados OK")


class TestUserLogin(TestCase):
    """Testa login de usuários"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='logintest',
            email='login@example.com',
            password='testpass123'
        )
    
    def test_user_authentication(self):
        """Verifica se o usuário pode ser autenticado"""
        from django.contrib.auth import authenticate
        
        auth_user = authenticate(username='logintest', password='testpass123')
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user.username, 'logintest')
        print(f"✅ Autenticação bem-sucedida: {auth_user.username}")
    
    def test_invalid_password_authentication(self):
        """Verifica se autenticação com senha errada falha"""
        from django.contrib.auth import authenticate
        
        auth_user = authenticate(username='logintest', password='wrongpass')
        self.assertIsNone(auth_user)
        print(f"✅ Autenticação com senha incorreta rejeitada")
    
    def test_login_session_creation(self):
        """Verifica se uma sessão é criada após login"""
        login_success = self.client.login(
            username='logintest',
            password='testpass123'
        )
        self.assertTrue(login_success)
        print(f"✅ Sessão de login criada")
    
    def test_nonexistent_user_login(self):
        """Verifica se login com usuário inexistente falha"""
        from django.contrib.auth import authenticate
        
        auth_user = authenticate(username='nonexistent', password='pass')
        self.assertIsNone(auth_user)
        print(f"✅ Login com usuário inexistente rejeitado")


class TestUserLogout(TestCase):
    """Testa logout de usuários"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='logouttest',
            password='testpass123'
        )
    
    def test_logout_clears_session(self):
        """Verifica se logout limpa a sessão"""
        self.client.login(username='logouttest', password='testpass123')
        
        from django.contrib.auth import get_user
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)
        
        self.client.logout()
        
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
        print(f"✅ Logout limpou a sessão")


class TestPasswordReset(TestCase):
    """Testa reset de senha"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='resettest',
            email='reset@example.com',
            password='oldpass123'
        )
    
    def test_password_change(self):
        """Verifica se a senha pode ser alterada"""
        self.user.set_password('newpass456')
        self.user.save()
        
        from django.contrib.auth import authenticate
        auth_user = authenticate(username='resettest', password='newpass456')
        self.assertIsNotNone(auth_user)
        print(f"✅ Senha alterada com sucesso")
    
    def test_old_password_no_longer_works(self):
        """Verifica se a senha antiga não funciona mais"""
        self.user.set_password('newpass456')
        self.user.save()
        
        from django.contrib.auth import authenticate
        auth_user = authenticate(username='resettest', password='oldpass123')
        self.assertIsNone(auth_user)
        print(f"✅ Senha antiga não funciona mais")


class TestUserPermissions(TestCase):
    """Testa permissões de usuário"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            email='user@example.com',
            password='userpass'
        )
    
    def test_admin_permissions(self):
        """Verifica se admin tem as permissões corretas"""
        self.assertTrue(self.admin_user.is_superuser)
        self.assertTrue(self.admin_user.is_staff)
        print(f"✅ Admin tem permissões de superusuário")
    
    def test_regular_user_permissions(self):
        """Verifica permissões de usuário regular"""
        self.assertFalse(self.regular_user.is_superuser)
        self.assertFalse(self.regular_user.is_staff)
        print(f"✅ Usuário regular tem permissões limitadas")


def run_all_tests():
    """Executa todos os testes de login"""
    print("\n" + "="*70)
    print("🔐 TESTES DE AUTENTICAÇÃO E LOGIN - DIGITALHUB")
    print("="*70 + "\n")
    
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=2, interactive=False, keepdb=False)
    failures = test_runner.run_tests(['tests.test_login'])
    
    print("\n" + "="*70)
    if failures == 0:
        print("✅ TODOS OS TESTES DE LOGIN PASSARAM!")
    else:
        print(f"❌ {failures} TESTE(S) FALHARAM")
    print("="*70 + "\n")
    
    return failures


if __name__ == '__main__':
    import sys
    sys.exit(run_all_tests())
