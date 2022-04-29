from django.urls import path
from . import views

app_name = 'ensino'

urlpatterns = [
    path('', views.MenuLinguasView.as_view(), name='menu_linguas'),
    path('lingua/<int:pk>', views.MenuLinguaView.as_view(), name='menu_lingua'),
    #
    path('lingua/<int:pk>/cadastro',
         views.AulaCadastroView.as_view(), name='cadastro_aula'),
    path('aula/<int:pk>', views.AulaView.as_view(), name='aula')
]
