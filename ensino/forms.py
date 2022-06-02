from cProfile import label
from re import A
from django.forms import inlineformset_factory
from django.forms.models import inlineformset_factory
from django.forms import modelformset_factory
from django import forms
from . import models


class LinguaCadastro(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    class Meta:
        model = models.Lingua
        fields = ('lingua', 'lingua_img')


class CriarAulaForms(forms.ModelForm):
    """
    Formulario para criacao de aula
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    class Meta:
        model = models.Aula
        fields = ('aula', 'conteudo',
                  'nivel', 'lingua', 'aula_gravada')
        widgets = {
            'aula': forms.TextInput(attrs={'placeholder': "Here comes class' name"}),
            'conteudo': forms.Textarea(attrs={'placeholder': "Now you can comment the subject which you have mentioned in your class' video"}),
        }


# class AtualizarAulaForms(forms.ModelForm):
#     """
#     Formulario para atualizacao de aula
#     """

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.label_suffix = ""
#         for field in self.Meta.unrequired:
#             self.fields[field].required = False

#     class Meta:
#         model = models.Aula
#         fields = ('aula', 'conteudo', 'conteudo_download', 'aula_gravada')

#         unrequired = {
#             'aula',
#             'conteudo',
#             'conteudo_download',
#             'aula_gravada',
#         }
# NOVOS CADASTROS

# A PALAVRA FORMS CONSIGO FAZER COMO O DE QUESTAO, E AUMENTAR QUANTIDADE DE CONTEXTO


class PalavraForms(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    contexto = forms.CharField(
        max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Let me give you an example.'}))

    class Meta:
        model = models.Palavra
        fields = ('palavra', 'lingua', 'nivel', 'classe', 'significado',
                  'escrita_fonetica')
        widgets = {
            'palavra': forms.TextInput(attrs={'placeholder': 'example '}),
            'significado': forms.TextInput(attrs={'placeholder': 'something that can explain another one'}),
            'escrita_fonetica': forms.TextInput(attrs={'placeholder': '/ɪɡˈzɑːmpl/'}),
        }


PalavraAulaForms = modelformset_factory(
    models.AulaPalavra, fields=('palavra',), extra=1,
)


class QuestaoForms(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    class Meta:
        model = models.Questao
        fields = ('frase', 'lingua', 'nivel',)
        widgets = {
            'frase': forms.TextInput(attrs={'placeholder': "Put here the ________ of phrase"})
        }


class AlternativaForms(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    class Meta:
        model = models.Alternativa
        fields = ('alternativa', 'is_correct', )
        widgets = {
            'alternativa': forms.TextInput(attrs={'placeholder': 'alternative'})
        }


AlternativasQuestaoFormset = inlineformset_factory(
    models.Questao,
    models.Alternativa,
    form=AlternativaForms,
    extra=1,
    can_delete=False
)

AlternativasFormFactory = modelformset_factory(
    models.Alternativa, fields=('alternativa', 'is_correct'), extra=1,
)
