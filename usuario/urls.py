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
    path('person_update', views.UpdateInformacoesView.as_view(), name='update_infos')
]
