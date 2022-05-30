from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('lingua/<int:pk>', views.ForumLinguaView.as_view(), name='forum_lingua'),
    path('lingua/postagem/registro/<int:pk>', views.PostagemRegistraView.as_view(),
         name='postagem_cadastro'),
    path('lingua/postagem/<int:pk>', views.PostagemView.as_view(), name='postagem'),
    path('noticia/cadastro', views.NoticiaCadastroView.as_view(),
         name='cadastro_noticia'),
    path('noticia/<int:pk>', views.NoticiaView.as_view(), name='noticia'),

]
