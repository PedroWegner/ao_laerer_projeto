from django.contrib import admin
from forum.models import Conversa, ConversaUsuario
from .models import *

admin.site.register(Usuario)
admin.site.register(Pessoa)
admin.site.register(Conversa)
admin.site.register(ConversaUsuario)
