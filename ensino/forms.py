from django.forms import inlineformset_factory
from django.forms.models import inlineformset_factory
from django.forms import modelformset_factory
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

# A PALAVRA FORMS CONSIGO FAZER COMO O DE QUESTAO, E AUMENTAR QUANTIDADE DE CONTEXTO


class PalavraForms(forms.ModelForm):
    contexto = forms.CharField(max_length=255)

    class Meta:
        model = models.Palavra
        fields = ('palavra', 'lingua', 'nivel', 'classe', 'significado',
                  'escrita_fonetica')


PalavraAulaForms = modelformset_factory(
    models.AulaPalavra, fields=('palavra',), extra=1,
)


class QuestaoForms(forms.ModelForm):
    class Meta:
        model = models.Questao
        fields = ('frase', 'lingua', 'nivel',)


class AlternativaForms(forms.ModelForm):
    class Meta:
        model = models.Alternativa
        fields = ('alternativa', 'is_correct', )


AlternativasQuestaoFormset = inlineformset_factory(
    models.Questao,
    models.Alternativa,
    form=AlternativaForms,
    extra=1,
    can_delete=False
)
