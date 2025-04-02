from django.shortcuts import render, redirect
import urllib.parse as urlparse
from .forms import PlaylistForm, PlaylistVideoForm
from django.contrib.auth.decorators import login_required
from .models import Playlist, Video, PlaylistVideo
from django.contrib.auth.models import User
from dotenv import load_dotenv
import os
import requests

load_dotenv()

@login_required(login_url='/auth/login')
def principal(request):
    return render(request, 'principal.html')


@login_required(login_url='/auth/login')
def cadastrar_playlist(request):
    if request.method == 'POST':
        formulario = PlaylistForm(request.POST)
        if formulario.is_valid():
            playlist = formulario.save(commit=False)
            playlist.autor = User.objects.get(usuario=request.user)
            playlist.save() 
            return redirect('principal')  
    else:
        formulario = PlaylistForm()  
        return render(request, 'cadastrar_playlist.html', {'formulario': formulario})


@login_required(login_url='/auth/login')
def minhas_playlists(request):
    usuario = request.user
    playlists_usuario = Playlist.objects.filter(autor=usuario)
    return render(request, 'minhas_playlists.html', {'playlists': playlists_usuario})

@login_required(login_url='/auth/login')
def cadastrar_playlist(request):
    if request.method == 'POST':
        formulario = PlaylistForm(request.POST)
        if formulario.is_valid():
            playlist = formulario.save(commit=False)
            playlist.autor = request.user
            playlist.save()
            return redirect('playlists')
    else:
        formulario = PlaylistForm()
    return render(request, 'cadastrar_playlist.html', {'formulario': formulario})

@login_required(login_url='/auth/login')
def editar_playlist(request, id):
    playlist = Playlist.objects.get(id=id)
    if request.method == 'POST':
        formulario = PlaylistForm(request.POST, instance=playlist)
        if formulario.is_valid():
            formulario.save()
            return redirect('playlists')

    formulario = PlaylistForm(instance=playlist)   
    return render(request, 'editar_playlist.html', {'formulario': formulario}) 

@login_required(login_url='/auth/login')
def excluir_playlist(request, id):
    playlist = Playlist.objects.get(id=id)
    playlist.delete()
    return redirect('playlists')

def extrair_id_video(url):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    parse_result = urlparse.urlparse(url)
    id_video = None

    if parse_result.netloc in ['www.youtube.com', 'youtube.com']:
        query = urlparse.parse_qs(parse_result.query)
        id_video = query['v'][0]
    elif parse_result.netloc == 'youtu.be':
        id_video = parse_result.path[1:]

    return id_video

def buscar_informacoes_video(id_video):
    url = os.getenv('YOUTUBE_API_URL')
    api_key = os.getenv('YOUTUBE_API_KEY')

    params = {
        'id': id_video,
        'key': api_key,
        'part': 'snippet'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar informações do vídeo: {e}")
        return None


@login_required(login_url='/auth/login')
def cadastrar_video(request, id):
    if request.method == "POST":
        formulario = PlaylistVideoForm(request.POST)
        if formulario.is_valid():
            url_video = formulario.cleaned_data.get('url_video')
            nivel_dificuldade = formulario.cleaned_data.get('nivel_dificuldade')
            
            id_video = extrair_id_video(url_video)
            video, created = Video.objects.get_or_create(youtube_id=id_video)

            # Se for um vídeo novo, busca informações na API
            if created:
                data = buscar_informacoes_video(id_video)
                if data and data.get("items"):
                    snippet = data["items"][0]["snippet"]
                    
                    print(snippet)
                    print(snippet.get("tags"))
                    
                    video.youtube_id = id_video
                    video.thumbnail = snippet.get("thumbnails").get("standard").get("url")
                    video.titulo = snippet.get("title")
                    video.canal = snippet.get("channelTitle")
                    video.save()


            playlist = Playlist.objects.get(id=id)
            if not PlaylistVideo.objects.filter(playlist=playlist, video=video).exists():
                PlaylistVideo.objects.create(
                    playlist=playlist,
                    video=video,
                    nivel_dificuldade=nivel_dificuldade
                )
            return redirect('detalhes_playlist', id)  

    else:
        formulario = PlaylistVideoForm()

    return render(request, "cadastrar_video.html", {"formulario": formulario, "playlist": playlist})

def excluir_video(request, id, id_video):
    playlist = Playlist.objects.get(id=id)
    video = Video.objects.get(id=id_video)
    playlist_video = PlaylistVideo.objects.get(playlist=playlist, video=video)
    playlist_video.delete()
    return redirect('detalhes_playlist', id)


def detalhes_playlist(request, id):
    playlist = Playlist.objects.get(id=id)
    videos = PlaylistVideo.objects.filter(playlist=playlist).select_related('video')
    formulario = PlaylistVideoForm()
    return render(request, 'detalhes_playlist.html', {'playlist': playlist, 'formulario': formulario, 'playlist_videos': videos})
