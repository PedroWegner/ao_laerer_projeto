from cProfile import label
from .models import *
from dataclasses import fields
from tkinter import Widget
from django import forms
from . import models


class PostagemForms(forms.ModelForm):
    class Meta:
        model = Postagem
        fields = ('titulo_postagem', 'conteudo_postagem',
                  'imagem_postagem')


class ComentarioForms(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ComentarioForms, self).__init__(*args, **kwargs)

        self.fields['conteudo_comentario'].label = "Comentário"

    class Meta:
        model = Comentario
        fields = ('conteudo_comentario', 'imagem_comentario')


class MensagemForms(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MensagemForms, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['texto'].label = ""

    class Meta:
        model = Mensagem
        fields = ('texto',)


class PublicarNoticiaForms(forms.ModelForm):
    class Meta:
        model = models.Noticia
        fields = ('titulo_noticia', 'conteudo_noticia', 'imagem_noticia')
