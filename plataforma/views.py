from django.shortcuts import render, redirect, get_object_or_404
import urllib.parse as urlparse
from .forms import PlaylistForm, PlaylistVideoForm, PerguntaForm, FormularioRespostaAlternativa, FormularioRespostaVerdadeiroFalso
from django.contrib.auth.decorators import login_required
from .models import Playlist, Video, PlaylistVideo, PerguntaAlternativas, PerguntaVerdadeiroFalso, Pergunta
from django.contrib.auth.models import User
from dotenv import load_dotenv
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string
import os
import requests


@login_required(login_url='/auth/login')
def principal(request):
    playlists = Playlist.objects.all()
    return render(request, 'principal.html', {'playlists': playlists})


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
    load_dotenv()
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
                if data:
                    snippet = data["items"][0]["snippet"]
                    
                    print(snippet)
                    # print(snippet.get("tags"))
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
    playlist_videos = PlaylistVideo.objects.filter(playlist=id)
    formulario = PlaylistVideoForm()
    return render(request, 'detalhes_playlist.html', {'playlist': playlist, 'formulario': formulario, 'playlist_videos': playlist_videos})

def cadastrar_pergunta(request, id, id_video):
    if request.method == 'POST':
        formulario = PerguntaForm(request.POST)
        print(formulario.errors)
        if formulario.is_valid():
            tipo_pergunta = formulario.cleaned_data['tipo_pergunta']
            pergunta = formulario.cleaned_data['pergunta']
            autor = request.user
            video_pergunta = PlaylistVideo.objects.get(playlist=id, video=id_video)
            print(tipo_pergunta, pergunta, autor, video_pergunta)
            if tipo_pergunta == 'alternativas':
                PerguntaAlternativas.objects.create(
                    pergunta=pergunta,
                    autor=autor,
                    video_pergunta=video_pergunta,
                    alternativa1=formulario.cleaned_data['alternativa1'],
                    alternativa2=formulario.cleaned_data['alternativa2'],
                    alternativa3=formulario.cleaned_data['alternativa3'],
                    alternativa4=formulario.cleaned_data['alternativa4'],
                    alternativa_correta=formulario.cleaned_data['alternativa_correta'])
            elif tipo_pergunta == 'verdadeiro_falso':
                PerguntaVerdadeiroFalso.objects.create(
                    pergunta=pergunta,
                    autor=autor,
                    video_pergunta=video_pergunta,
                    resposta=formulario.cleaned_data['resposta']
                )
            return redirect('perguntas_video', id, id_video)
        else:

            playlist_video = get_object_or_404(PlaylistVideo, playlist=id, video=id_video)
            perguntas_alternativas = PerguntaAlternativas.objects.filter(video_pergunta=playlist_video)    
            perguntas_verdadeiro_falso = PerguntaVerdadeiroFalso.objects.filter(video_pergunta=playlist_video)
            return render(request, 'perguntas_video.html', 
                {        
                    'playlist_video': playlist_video,
                    'formulario': formulario, 
                    'perguntas_alternativas': perguntas_alternativas,
                    'perguntas_verdadeiro_falso': perguntas_verdadeiro_falso,
                })   

    return redirect('perguntas_video', id, id_video)
    

def perguntas_video(request, id, id_video, playlist_video=None):
    playlist_video = get_object_or_404(PlaylistVideo, playlist=id, video=id_video)
    perguntas_alternativas = PerguntaAlternativas.objects.filter(video_pergunta=playlist_video)    
    perguntas_verdadeiro_falso = PerguntaVerdadeiroFalso.objects.filter(video_pergunta=playlist_video)
    formulario = PerguntaForm()

    return render(request, 'perguntas_video.html', 
        {        
            'playlist_video': playlist_video,
            'formulario': formulario, 
            'perguntas_alternativas': perguntas_alternativas,
            'perguntas_verdadeiro_falso': perguntas_verdadeiro_falso,
        })    

def excluir_pergunta(request, id, id_video, id_pergunta):
    pergunta = PerguntaAlternativas.objects.filter(id=id_pergunta).first()
    if pergunta:
        pergunta.delete()
    else:
        pergunta = PerguntaVerdadeiroFalso.objects.get(id=id_pergunta)
        pergunta.delete()
    
    return redirect('perguntas_video', id, id_video)


def get_perguntas_video(request, id, id_playlist_video):
    playlist_video = get_object_or_404(PlaylistVideo, id=id_playlist_video)
    print(id_playlist_video)
    print(playlist_video)
    perguntas_alternativas = PerguntaAlternativas.objects.filter(video_pergunta=playlist_video)
    perguntas_vf = PerguntaVerdadeiroFalso.objects.filter(video_pergunta=playlist_video)

    perguntas = []
    for pergunta in perguntas_alternativas:
        perguntas.append({
            'id': pergunta.id,
            'tipo': 'alternativas',
            'pergunta': pergunta.pergunta,
            'alternativas': [pergunta.alternativa1, pergunta.alternativa2, pergunta.alternativa3, pergunta.alternativa4],
            'alternativa_correta': pergunta.alternativa_correta
        })
    for pergunta in perguntas_vf:
        perguntas.append({
            'id': pergunta.id,
            'tipo': 'verdadeiro_falso',
            'pergunta': pergunta.pergunta,
            'resposta': pergunta.resposta
        })

    return JsonResponse({'perguntas': perguntas})


def get_formulario_resposta(request, id_pergunta):
    try:
        # Tenta obter uma pergunta do tipo alternativas
        pergunta = PerguntaAlternativas.objects.get(id=id_pergunta)
        alternativas = [
            pergunta.alternativa1,
            pergunta.alternativa2,
            pergunta.alternativa3,
            pergunta.alternativa4
        ]
        formulario = FormularioRespostaAlternativa(
            alternativas=alternativas,
            initial={'pergunta_id': pergunta.id}
        )
    except PerguntaAlternativas.DoesNotExist:
        pergunta = get_object_or_404(PerguntaVerdadeiroFalso, id=id_pergunta)
        formulario = FormularioRespostaVerdadeiroFalso(
            initial={'pergunta_id': pergunta.id}
        )

    formulario_html = formulario.as_p()
    return JsonResponse({'formulario_html': formulario_html})        


def assistir_playlist(request, id, index_video=0):
    playlist = get_object_or_404(Playlist, id=id)
    playlist_videos = PlaylistVideo.objects.filter(playlist=playlist)

    if playlist_videos.exists():
        video_atual = playlist_videos.first()

    context = {
        'playlist': playlist,
        'playlist_videos': playlist_videos,
        'video_atual': video_atual
    }

    return render(request, 'assistir_playlist.html', context)


def checar_resposta(request):
    print(request)
    print("logica de checagem de resposta")
    if request.method == 'POST':
        pergunta_id = request.POST.get('pergunta_id')
        resposta = request.POST.get('resposta')
        # Apenas verificando o envio da resposta, sem validacao ainda
        return JsonResponse({'status': 'success', 'mensagem': 'Resposta recebida'})
    return JsonResponse({'status': 'error', 'mensagem': 'Método inválido'}) 