from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario


class FormCadastro(UserCreationForm):
    email = forms.EmailField(required=True, label='E-mail')

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']
        labels = {'username': 'Nome de usuário'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})


class FormLogin(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})


class FormContato(forms.Form):
    nome    = forms.CharField(max_length=100, label='Nome')
    email   = forms.EmailField(label='E-mail')
    assunto = forms.CharField(max_length=200, label='Assunto')
    mensagem = forms.CharField(widget=forms.Textarea, label='Mensagem')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})
        self.fields['mensagem'].widget.attrs.update({'rows': 5})