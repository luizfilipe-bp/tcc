from django.contrib import admin
from .models import Perfil, Playlist, Video, PlaylistVideo

class PerfilAdmin(admin.ModelAdmin):
    list_display = (['usuario'])

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nivel_dificuldade', 'categoria', 'autor')

class VideoAdmin(admin.ModelAdmin):
    list_display = ('youtube_id', 'titulo', 'canal')

class PlaylistVideoAdmin(admin.ModelAdmin):
    list_display = ('playlist', 'video', 'nivel_dificuldade')

admin.site.register(Perfil, PerfilAdmin)
admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(PlaylistVideo, PlaylistVideoAdmin)