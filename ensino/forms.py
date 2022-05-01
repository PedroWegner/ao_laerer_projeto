from ast import Mod
from typing import Type
from .models import Aula
from dataclasses import fields
from tkinter import Widget
from django import forms
from . import models


class LinguaCadastro(forms.ModelForm):
    class Meta:
        model = models.Lingua
        fields = ('lingua', 'lingua_img')


class AtividadePostagemForms(forms.ModelForm):
    """ 
    Formulario para postagem de atividades
    """
    class Meta:
        model = models.Atividade
        fields = ('atividade_doc', 'comentario')


class AtividadeEnviadaForms(forms.ModelForm):
    """
    Formulario para envio de atividades
    """
    class Meta:
        model = models.EnvioAtividade
        fields = ('envio_atividade_doc', )

# VERIFICAR FORMS ABAIXO


class AtribuiNotaAtividadeForms(forms.ModelForm):
    class Meta:
        model = models.EnvioAtividade
        fields = ('nota', )


#
class CriarAulaForms(forms.ModelForm):
    """
    Formulario para criacao de aula
    """
    class Meta:
        model = models.Aula
        fields = ('aula', 'conteudo', 'conteudo_download',
                  'nivel', 'lingua', 'aula_gravada')


class CriarAtividadeForms(forms.ModelForm):
    """
    Formulario para a criacao de atividae, chamado na mesma view do form de aula
    """
    class Meta:
        model = models.Atividade
        fields = ('atividade_doc', 'comentario')


class AtualizarAulaForms(forms.ModelForm):
    """
    Formulario para atualizacao de aula
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.unrequired:
            self.fields[field].required = False

    # aula = forms.CharField(required=False)
    # aula_gravada = forms.FileField(required=False)
    # conteudo_download = forms.FileField(required=False)
    # conteudo = forms.CharField(required=False)

    class Meta:
        model = models.Aula
        fields = ('aula', 'conteudo', 'conteudo_download', 'aula_gravada')

        unrequired = {
            'aula',
            'conteudo',
            'conteudo_download',
            'aula_gravada',
        }


class AtualizarAtividadeAluno(forms.ModelForm):
    class Meta:
        model = models.EnvioAtividade
        fields = ('envio_atividade_doc', 'envio_definitivo',)

# NOVOS CADASTROS


class PalavraForms(forms.ModelForm):
    contexto = forms.CharField(max_length=255)

    class Meta:
        model = models.Palavra
        fields = ('palavra', 'classe', 'significado',
                  'nivel', 'escrita_fonetica')
