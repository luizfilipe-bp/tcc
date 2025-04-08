from django.urls import path
from . import views

urlpatterns = [
    path('', views.principal, name='principal'),
    path('playlists', views.minhas_playlists, name='playlists'),
    path('playlists/cadastrar', views.cadastrar_playlist, name='cadastrar_playlist'),
    path('playlists/editar/<int:id>', views.editar_playlist, name='editar_playlist'),
    path('playlists/excluir/<int:id>', views.excluir_playlist, name='excluir_playlist'),
    path('playlists/<int:id>/', views.detalhes_playlist, name='detalhes_playlist'),
    path('playlists/<int:id>/cadastrar_video', views.cadastrar_video, name='cadastrar_video'),
    path('playlists/<int:id>/excluir_video/<int:id_video>', views.excluir_video, name='excluir_video'),
    path('playlists/<int:id>/perguntas_video/<int:id_video>', views.perguntas_video, name='perguntas_video'),
    path('playlists/<int:id>/perguntas_video/<int:id_video>/cadastrar_pergunta', views.cadastrar_pergunta, name='cadastrar_pergunta'),
    path('playlists/<int:id>/perguntas_video/<int:id_video>/excluir_pergunta/<int:id_pergunta>', views.excluir_pergunta, name='excluir_pergunta'),
    path('playlists/<int:id>/assistir/<int:index_video>', views.assistir_playlist, name='assistir_playlist'),
    path('playlists/<int:id>/assistir/get_perguntas_video/<int:id_playlist_video>', views.get_perguntas_video, name='get_perguntas_video'),

    path('checar_resposta', views.checar_resposta, name='checar_resposta'),
    path('get_formulario_resposta/<int:id_pergunta>', views.get_formulario_resposta, name='get_formulario_resposta'),
]