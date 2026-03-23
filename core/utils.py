# core/utils.py
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def _html_confirmacao(pedido, usuario):
    itens_html = ''
    for item in pedido.itens.all():
        itens_html += f'''
        <tr>
          <td style="padding:8px 24px;border-top:1px solid #e4e4ee;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="font-size:0.9rem;font-weight:500;color:#18181f;">{item.produto.nome}</td>
                <td align="right" style="font-size:0.9rem;font-weight:600;color:#0050e6;white-space:nowrap;">R$ {item.preco:.2f}</td>
              </tr>
            </table>
          </td>
        </tr>'''

    nome = usuario.first_name or usuario.username
    url_conta = f"{settings.SITE_URL}/minha-conta/"

    return f'''<!DOCTYPE html>
<html lang="pt-br">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background-color:#f5f7ff;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f5f7ff;padding:40px 0;">
  <tr><td align="center">
    <table width="560" cellpadding="0" cellspacing="0" border="0" style="background-color:#ffffff;border-radius:16px;overflow:hidden;">

      <tr>
        <td align="center" style="background-color:#0050e6;padding:32px 40px;">
          <p style="margin:0 0 6px 0;font-size:2rem;">✅</p>
          <p style="margin:0;font-size:1.1rem;font-weight:700;color:#ffffff;">DigitalHub</p>
        </td>
      </tr>

      <tr>
        <td style="padding:36px 40px;">
          <h1 style="margin:0 0 10px 0;font-size:1.4rem;font-weight:700;color:#0d0d12;">Compra confirmada!</h1>
          <p style="margin:0 0 24px 0;font-size:0.9rem;color:#6e6e82;line-height:1.7;">
            Olá, <strong style="color:#18181f;">{nome}</strong>! Seu pedido foi processado com sucesso.
          </p>

          <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f8f8fc;border:1px solid #e4e4ee;border-radius:12px;margin-bottom:20px;">
            <tr>
              <td style="padding:16px 24px 8px 24px;">
                <p style="margin:0;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.09em;color:#9898aa;">
                  Pedido #{pedido.id} — {pedido.criado_em.strftime("%d/%m/%Y")}
                </p>
              </td>
            </tr>
            {itens_html}
            <tr>
              <td style="padding:14px 24px;border-top:2px solid #e4e4ee;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td style="font-size:0.9rem;font-weight:600;color:#18181f;">Total pago</td>
                    <td align="right" style="font-size:1.1rem;font-weight:700;color:#0d0d12;">R$ {pedido.total:.2f}</td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>

          <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;margin-bottom:20px;">
            <tr>
              <td style="padding:12px 16px;font-size:0.85rem;color:#16a34a;font-weight:500;">
                🛡️ Garantia de 7 dias — se não ficar satisfeito, devolvemos seu dinheiro.
              </td>
            </tr>
          </table>

          <table cellpadding="0" cellspacing="0" border="0" style="margin-bottom:20px;">
            <tr>
              <td style="background-color:#0050e6;border-radius:8px;">
                <a href="{url_conta}" style="display:inline-block;padding:12px 24px;font-size:0.9rem;font-weight:600;color:#ffffff;text-decoration:none;">
                  Acessar minha conta →
                </a>
              </td>
            </tr>
          </table>

          <p style="margin:0;font-size:0.85rem;color:#6e6e82;">
            Dúvidas? <a href="mailto:contato@digitalhub.com" style="color:#0050e6;">contato@digitalhub.com</a>
          </p>
        </td>
      </tr>

      <tr>
        <td align="center" style="background-color:#f8f8fc;border-top:1px solid #e4e4ee;padding:20px 40px;">
          <p style="margin:0;font-size:0.75rem;color:#9898aa;">
            Você recebeu este e-mail porque realizou uma compra na DigitalHub.
          </p>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>'''


def _html_boas_vindas(usuario):
    nome = usuario.first_name or usuario.username
    url_produtos = f"{settings.SITE_URL}/produtos/"

    return f'''<!DOCTYPE html>
<html lang="pt-br">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background-color:#f5f7ff;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f5f7ff;padding:40px 0;">
  <tr><td align="center">
    <table width="560" cellpadding="0" cellspacing="0" border="0" style="background-color:#ffffff;border-radius:16px;overflow:hidden;">

      <tr>
        <td align="center" style="background-color:#0d0d12;padding:32px 40px;">
          <p style="margin:0 0 6px 0;font-size:2rem;">👋</p>
          <p style="margin:0;font-size:1.1rem;font-weight:700;color:#ffffff;">DigitalHub</p>
        </td>
      </tr>

      <tr>
        <td style="padding:36px 40px;">
          <h1 style="margin:0 0 10px 0;font-size:1.4rem;font-weight:700;color:#0d0d12;">Bem-vindo, {nome}!</h1>
          <p style="margin:0 0 24px 0;font-size:0.9rem;color:#6e6e82;line-height:1.7;">
            Sua conta foi criada com sucesso. Acesse milhares de produtos digitais criados por especialistas.
          </p>

          <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f8f8fc;border:1px solid #e4e4ee;border-radius:10px;margin-bottom:10px;">
            <tr><td style="padding:14px 16px;">
              <table cellpadding="0" cellspacing="0" border="0"><tr>
                <td style="font-size:1.2rem;padding-right:10px;vertical-align:top;">🎓</td>
                <td>
                  <p style="margin:0 0 2px 0;font-size:0.875rem;font-weight:600;color:#18181f;">Cursos completos</p>
                  <p style="margin:0;font-size:0.8rem;color:#9898aa;">Aprenda com instrutores especializados em diversas áreas.</p>
                </td>
              </tr></table>
            </td></tr>
          </table>

          <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f8f8fc;border:1px solid #e4e4ee;border-radius:10px;margin-bottom:10px;">
            <tr><td style="padding:14px 16px;">
              <table cellpadding="0" cellspacing="0" border="0"><tr>
                <td style="font-size:1.2rem;padding-right:10px;vertical-align:top;">📚</td>
                <td>
                  <p style="margin:0 0 2px 0;font-size:0.875rem;font-weight:600;color:#18181f;">E-books e templates</p>
                  <p style="margin:0;font-size:0.8rem;color:#9898aa;">Materiais práticos para acelerar seu crescimento.</p>
                </td>
              </tr></table>
            </td></tr>
          </table>

          <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f8f8fc;border:1px solid #e4e4ee;border-radius:10px;margin-bottom:24px;">
            <tr><td style="padding:14px 16px;">
              <table cellpadding="0" cellspacing="0" border="0"><tr>
                <td style="font-size:1.2rem;padding-right:10px;vertical-align:top;">⚡</td>
                <td>
                  <p style="margin:0 0 2px 0;font-size:0.875rem;font-weight:600;color:#18181f;">Acesso imediato</p>
                  <p style="margin:0;font-size:0.8rem;color:#9898aa;">Após a compra, acesse seus produtos instantaneamente.</p>
                </td>
              </tr></table>
            </td></tr>
          </table>

          <table cellpadding="0" cellspacing="0" border="0" style="margin-bottom:20px;">
            <tr>
              <td style="background-color:#0050e6;border-radius:8px;">
                <a href="{url_produtos}" style="display:inline-block;padding:12px 24px;font-size:0.9rem;font-weight:600;color:#ffffff;text-decoration:none;">
                  Explorar produtos →
                </a>
              </td>
            </tr>
          </table>

          <p style="margin:0;font-size:0.85rem;color:#6e6e82;">
            Dúvidas? <a href="mailto:contato@digitalhub.com" style="color:#0050e6;">contato@digitalhub.com</a>
          </p>
        </td>
      </tr>

      <tr>
        <td align="center" style="background-color:#f8f8fc;border-top:1px solid #e4e4ee;padding:20px 40px;">
          <p style="margin:0;font-size:0.75rem;color:#9898aa;">
            Você recebeu este e-mail porque criou uma conta na DigitalHub.
          </p>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>'''


def enviar_email_confirmacao_compra(pedido):
    usuario = pedido.usuario
    html    = _html_confirmacao(pedido, usuario)

    email = EmailMultiAlternatives(
        subject=f'✅ Compra confirmada — Pedido #{pedido.id}',
        body=f'Olá {usuario.username}, sua compra foi confirmada! Pedido #{pedido.id} — Total: R$ {pedido.total:.2f}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[usuario.email],
    )
    email.attach_alternative(html, 'text/html')
    email.send(fail_silently=False)


def enviar_email_boas_vindas(usuario):
    html = _html_boas_vindas(usuario)

    email = EmailMultiAlternatives(
        subject='👋 Bem-vindo à DigitalHub!',
        body=f'Olá {usuario.username}, sua conta foi criada com sucesso!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[usuario.email],
    )
    email.attach_alternative(html, 'text/html')
    email.send(fail_silently=False)