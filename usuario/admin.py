from django.contrib import admin

from forum.models import Conversa, ConversaUsuario
from .models import *
# Register your models here.
admin.site.register(Usuario)
admin.site.register(Pessoa)
admin.site.register(Endereco)
admin.site.register(Conversa)
admin.site.register(ConversaUsuario)
