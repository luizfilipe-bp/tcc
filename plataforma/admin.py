from django.contrib import admin
from .models import Perfil, Playlist, Video, PlaylistVideo, PerguntaAlternativas, PerguntaVerdadeiroFalso, ProgressoVideo, TipoConquista, Conquista

class PerfilAdmin(admin.ModelAdmin):
    list_display = (['usuario'])

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nivel_dificuldade', 'categoria', 'autor')

class VideoAdmin(admin.ModelAdmin):
    list_display = ('youtube_id', 'titulo', 'canal')

class PlaylistVideoAdmin(admin.ModelAdmin):
    list_display = ('playlist', 'video', 'nivel_dificuldade')

class PerguntaAlternativasAdmin(admin.ModelAdmin):
    list_display = ('pergunta', 'alternativa1', 'alternativa2', 'alternativa3', 'alternativa4', 'alternativa_correta')

class PerguntaVerdadeiroFalsoAdmin(admin.ModelAdmin):
    list_display = ('pergunta', 'resposta')

class ProgressoVideoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'playlist_video', 'video_completo', 'perguntas_respondidas')

class TipoConquistaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', 'xp')

class ConquistaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'usuario', 'data_conquista')

admin.site.register(Perfil, PerfilAdmin)
admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(PlaylistVideo, PlaylistVideoAdmin)
admin.site.register(PerguntaAlternativas, PerguntaAlternativasAdmin)
admin.site.register(PerguntaVerdadeiroFalso, PerguntaVerdadeiroFalsoAdmin)
admin.site.register(ProgressoVideo, ProgressoVideoAdmin)
admin.site.register(TipoConquista, TipoConquistaAdmin)
admin.site.register(Conquista, ConquistaAdmin)