from django.urls import path
from . import views

app_name = 'ensino'

urlpatterns = [
    path('', views.MenuLinguasView.as_view(), name='menu_linguas'),
    path('lingua/<int:pk>', views.MenuLinguaView.as_view(), name='menu_lingua'),
    path('lingua/<int:pk>/nivel/<int>/', views.MenuLinguaNivelView.as_view()),
    #
    path('aula/cadastro',
         views.AulaCadastroView.as_view(), name='cadastro_aula'),
    path('aula/<int:pk>', views.AulaView.as_view(), name='aula'),
    #
    path('lingua/cadastro', views.LinguaCadastroView.as_view(),
         name='cadastro_lingua'),
    path('minhas_aulas', views.MeuPainelAulasView.as_view(),
         name='minhas_aulas'),
    path('minhas_aulas/aula/<int:pk>',
         views.AtualizarAulaView.as_view(), name='atualizar_aula'),
    path('lingua/<int:pk>/palavra/cadastro', views.CadastraPalavraView.as_view(),
         name='palavra_cadastro'),
    path('lingua/<int:pk>/dicionario',
         views.LinguaDicionarioView.as_view(), name='dicionario'),
    path('lingua/palavra/<int:pk>/', views.PalavraView.as_view(), name='palavra'),
    path('aula/atividade/cadastro/<int:pk>',
         views.AtividadeUsuarioCadastroView.as_view(), name='enviar_atividade'),
    path('aula/atividade/atualizar/<int:pk>',
         views.AtividadeAlunoAtualizarView.as_view(), name='reenviar_atividade'),
]
