from django.urls import path
from . import views

app_name = 'ensino'

urlpatterns = [
    path('', views.MenuLinguasView.as_view(), name='menu_linguas'),
    path('lingua/<int:pk>', views.MenuLinguaView.as_view(), name='menu_lingua'),
    path('aula/cadastro',
         views.AulaCadastroView.as_view(), name='cadastro_aula'),
    path('aula/<int:pk>', views.AulaView.as_view(), name='aula'),
    path('lingua/cadastro', views.LinguaCadastroView.as_view(),
         name='cadastro_lingua'),
    path('meu_ensino', views.TesteMeuPainelAulasView.as_view(),
         name='minhas_aulas'),
    path('minhas_aulas/aula/<int:pk>',
         views.AtualizarAulaView.as_view(), name='atualizar_aula'),
    path('meu_ensino/palavra/cadastro', views.CadastraPalavraView.as_view(),
         name='palavra_cadastro'),
    path('lingua/<int:pk>/dicionario',
         views.LinguaDicionarioView.as_view(), name='dicionario'),
    path('lingua/palavra/<int:pk>/', views.PalavraView.as_view(), name='palavra'),
    #     path('minhas_aulas/aula/<int:pk>/add_palavra',
    #          views.AdicionaPalavraAula.as_view(), name='palavra_aula'),
    path('aula/atividade/<int:pk>', views.ResolucaoAtividade.as_view()),
    path('aula/redo/atividade/<int:pk>',
         views.UpdateAtividadeConcluida.as_view()),
    path('criar_questao', views.CriaQuestao.as_view(), name='add_questao'),
    path('questao/<int:pk>', views.ResolucaoQuestao.as_view()),
    path('minhas_aulas/aula/<int:pk>/adiciona_atividade',
         views.AdicionaAtividadeAula.as_view()),
    path('questao-update/<int:pk>', views.UpdateQuestao.as_view()),
    path('lingua/modulo/<int:pk>', views.ModuloView.as_view()),
    path('busca/<int:pk>/', views.BuscaView.as_view(), name='busca'),
    path('minhas_aulas/aula/<int:pk>/add_palavra', views.AddPalavra.as_view())
]
