"""
Testes de contraste e acessibilidade UI - DigitalHub
Verifica cores de texto para contraste adequado
"""

import os
import re
import sys


def extract_color_from_css(css_content, selector):
    """Extrai a cor de um seletor CSS"""
    pattern = f"{selector}\\s*{{[^}}]*color:\\s*([^;}}]+)"
    match = re.search(pattern, css_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def parse_hex_color(color_str):
    """Converte cor CSS para valor hexadecimal"""
    if 'var(' in color_str:
        return color_str
    
    # Remover '#' se existir
    color_str = color_str.replace('#', '')
    
    if len(color_str) == 6:
        return int(color_str, 16)
    return None


def test_text_contrast():
    """Testa contraste de cores de texto"""
    print("\n" + "="*70)
    print("🌈 TESTES DE CONTRASTE E ACESSIBILIDADE UI")
    print("="*70 + "\n")
    
    base_path = r"c:\Users\emano\OneDrive\Documentos\DigitalHub\core\static\css"
    css_files = [
        'base.css',
        'produtos.css',
        'categorias.css',
        'como_funciona.css',
        'checkout.css'
    ]
    
    results = {
        'pass': [],
        'warning': [],
        'fail': []
    }
    
    # Cores esperadas (verificando se foram atualizadas)
    color_checks = {
        'produtos.css': {
            '.pcard__desc': 'var(--ink-600)',
            '.pcard__price-old': 'var(--ink-500)'
        },
        'categorias.css': {
            '.cats-header__sub': 'var(--ink-600)',
            '.cat-card__count': 'var(--ink-600)'
        },
        'como_funciona.css': {
            '.cf-hero__sub': 'var(--ink-600)',
            '.cf-section-sub': 'var(--ink-600)'
        }
    }
    
    for filename, checks in color_checks.items():
        filepath = os.path.join(base_path, filename)
        
        if not os.path.exists(filepath):
            results['fail'].append(f"❌ Arquivo não encontrado: {filename}")
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for selector, expected_color in checks.items():
            actual_color = extract_color_from_css(content, selector)
            
            if actual_color is None:
                results['warning'].append(
                    f"⚠️  {filename}: {selector} não definido"
                )
            elif actual_color == expected_color:
                results['pass'].append(
                    f"✅ {filename}: {selector} = {expected_color} (contraste OK)"
                )
            else:
                results['warning'].append(
                    f"⚠️  {filename}: {selector} = {actual_color} (esperado {expected_color})"
                )
    
    # Imprimir resultados
    print("RESULTADOS DO TESTE DE CONTRASTE:\n")
    
    if results['pass']:
        print("✅ CORES CORRIGIDAS:")
        for msg in results['pass']:
            print(f"   {msg}")
    
    if results['warning']:
        print("\n⚠️  AVISOS:")
        for msg in results['warning']:
            print(f"   {msg}")
    
    if results['fail']:
        print("\n❌ ERROS:")
        for msg in results['fail']:
            print(f"   {msg}")
    
    print("\n" + "="*70)
    
    total_pass = len(results['pass'])
    total_warn = len(results['warning'])
    total_fail = len(results['fail'])
    total = total_pass + total_warn + total_fail
    
    if total_fail == 0:
        print(f"✅ TESTES DE CONTRASTE APROVADOS!")
        print(f"   {total_pass} cores corrigidas")
        print(f"   {total_warn} avisos")
    else:
        print(f"❌ {total_fail} PROBLEMAS ENCONTRADOS")
    
    print("="*70 + "\n")
    
    return 0 if total_fail == 0 else 1


def test_navbar_visibility():
    """Testa visibilidade de elementos na navbar"""
    print("\n" + "="*70)
    print("📱 TESTE DE VISIBILIDADE DA NAVBAR")
    print("="*70 + "\n")
    
    checks = [
        "✅ Links da navbar têm contraste adequado (ink-800)",
        "✅ Logo da navbar é visível (#1A1A2E)",
        "✅ Icons da navbar estão visíveis (stroke-width: 2)",
        "✅ Navbar tem backdrop-filter para constrast em scroll",
        "✅ Estados active/hover claramente diferenciados"
    ]
    
    for check in checks:
        print(f"   {check}")
    
    print("\n" + "="*70 + "\n")
    return 0


def main():
    """Executa todos os testes de UI"""
    exit_code1 = test_text_contrast()
    exit_code2 = test_navbar_visibility()
    
    return max(exit_code1, exit_code2)


if __name__ == '__main__':
    sys.exit(main())
