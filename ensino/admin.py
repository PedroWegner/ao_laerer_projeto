from ast import Mod
from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Lingua)
admin.site.register(NivelLingua)
admin.site.register(ClassePalavra)
admin.site.register(Aula)
admin.site.register(AulaPalavra)
admin.site.register(Questao)
admin.site.register(AtividadeAula)
admin.site.register(AtividadeQuestao)
admin.site.register(Alternativa)
admin.site.register(UsuarioLingua)
admin.site.register(ModuloLinguaNivel)
admin.site.register(EnvioAtividadeAula)
