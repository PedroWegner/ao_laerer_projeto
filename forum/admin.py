from django.contrib import admin

from forum.models import Conversa, Mensagem, Noticia

# Register your models here.
admin.site.register(Mensagem)
admin.site.register(Noticia)
