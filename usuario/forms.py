from django import forms
import re
from . import models
from utils.valida_cpf import valida_cpf
import bcrypt


class UsuarioLogin(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
    usuario = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'user_name'})
    )
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '••••••'})
    )


class UsuarioCadastro(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    class Meta:
        model = models.Usuario
        fields = (
            'usuario',
            'email',
            'senha',
        )
        widgets = {
            'usuario': forms.TextInput(attrs={'placeholder': 'user_name'}),
            'email': forms.TextInput(attrs={'placeholder': 'email@email.com'}),
            'senha': forms.PasswordInput(attrs={'placeholder': '••••••'}),
        }

    def save(self, commit=True):
        usuario = super(UsuarioCadastro, self).save(commit=False)
        data = self.cleaned_data
        senha = data['senha']
        senha_criptografada = bcrypt.hashpw(
            (senha).encode('utf-8'), bcrypt.gensalt()
        )
        usuario.senha = str(senha_criptografada)[2:-1]
        if commit:
            usuario.save()
        return usuario


class PessoaCadastro(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    class Meta:
        model = models.Pessoa
        fields = (
            'nome',
            'sobrenome',
            'data_nascimento',
        )
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'your name'}),
            'sobrenome': forms.TextInput(attrs={'placeholder': 'your surname'}),
            'data_nascimento': forms.TextInput(attrs={'placeholder': '15/06/2001'}),
        }


# class AtualizarPessoa(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.label_suffix = ""
#         for field in self.Meta.unrequired:
#             self.fields[field].required = False

#     class Meta:
#         model = models.Pessoa
#         fields = (
#             'nome',
#             'sobrenome',
#         )

#         unrequired = (
#             'nome',
#             'sobrenome',
#         )


# class AtualizarUsuario(forms.ModelForm):
#     class Meta:
#         model = models.Usuario
#         fields = ('img_usuario', )


# class AtualizarSenha(forms.ModelForm):

#     class Meta:
#         model = models.Usuario
#         fields = ('senha', )

#     def clean(self, *args, **kwargs):
#         cleaned = self.cleaned_data
#         validation_error = {

#         }

#         senha_antiga_1 = self.cleaned_data.get('senha_antiga_1')
#         senha_antiga_2 = self.cleaned_data.get('senha_antiga_2')

#         if senha_antiga_1 != senha_antiga_2:
#             validation_error['senha_antiga_1'] = "Senhas diferentes"
#             validation_error['senha_antiga_2'] = "Senhas diferentes"

#         if validation_error:
#             raise(forms.ValidationError(validation_error))
