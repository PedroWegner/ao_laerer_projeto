from django.urls import path
from . import views

app_name = 'usuario'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('cadastro/', views.UsuarioCadastroView.as_view(), name='usuario_cadastro'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout')
]
