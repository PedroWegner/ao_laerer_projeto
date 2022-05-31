from django.urls import path
from . import views

app_name = 'usuario'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('cadastro/', views.UsuarioCadastroView.as_view(), name='usuario_cadastro'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('perfil/<int:pk>',
         views.PerfilUsuarioView.as_view(), name='perfil_usuario'),
    path('perfil/conversa/<int:pk>',
         views.ConversaView.as_view(), name='conversa'),
    path('perfil/cad/conv/<int:pk>',
         views.IniciaConversa.as_view(), name='ini_conv'),
    path('dados/atualizar', views.DadosAtualizarView.as_view(),
         name='atualizar_dados'),
    path('senha/atualizar', views.SenhaAtualizarView.as_view(),
         name='atualizar_senha'),
    path('usuario/<int:pk>/atualizar', views.UsuarioAtualizarView.as_view(),
         name='atualizar_usuario'),
    #
    path('teste/<int:pk>/atualizar',
         views.TesteAtualizaFotoView.as_view(), name='teste')
]
