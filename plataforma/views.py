from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
import urllib.parse as urlparse
from .forms import PlaylistForm, PlaylistVideoForm, PerguntaForm, FormularioRespostaAlternativa, FormularioRespostaVerdadeiroFalso
from django.contrib.auth.decorators import login_required
from .models import Playlist, Video, PlaylistVideo, Pergunta, PerguntaAlternativas, PerguntaVerdadeiroFalso, ProgressoVideo, ProgressoPergunta, TipoConquista, Conquista
from django.contrib.auth.models import User
from dotenv import load_dotenv
from django.http import JsonResponse
import os
import requests
from django.views.decorators.http import require_POST



@login_required(login_url='/auth/login')
def principal(request):
    playlists = Playlist.objects.all()
    return render(request, 'principal.html', {'playlists': playlists})


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

            verificarConquistaCursosCriados(request.user)

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

            verificarConquistaPerguntasCriadas(request.user)
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
    pergunta = PerguntaAlternativas.objects.filter(id=id_pergunta).first()
    if pergunta:
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
    else:
        pergunta = get_object_or_404(PerguntaVerdadeiroFalso, id=id_pergunta)
        formulario = FormularioRespostaVerdadeiroFalso(
            initial={'pergunta_id': pergunta.id}
        )

    formulario_html = formulario.as_p()
    return JsonResponse({'formulario_html': formulario_html})        


def finalizou_playlist(request, id):
    playlist = get_object_or_404(Playlist, id=id)
    return render(request, 'finalizou_playlist.html', {'playlist': playlist})
     

def assistir_playlist(request, id, index_video=0):
    playlist = get_object_or_404(Playlist, id=id)
    playlist_videos = PlaylistVideo.objects.filter(playlist=playlist)
    video_atual = None
    if playlist_videos.exists():
        if 0 <= index_video and  not (index_video > len(playlist_videos) - 1):
            video_atual = playlist_videos[index_video]
            context = {
                'playlist': playlist,
                'playlist_videos': playlist_videos,
                'video_atual': video_atual,
                'index_video': index_video,
            }
            return render(request, 'assistir_playlist.html', context)
        else:
            return redirect('finalizou_playlist', id)

def checar_resposta(request):
    pergunta_id = request.POST.get('pergunta_id')
    resposta = request.POST.get('resposta')


    pergunta = PerguntaAlternativas.objects.filter(id=pergunta_id).first()
    if pergunta:
        resposta_correta = str(pergunta.alternativa_correta)
        alternativas = [
            pergunta.alternativa1,
            pergunta.alternativa2,
            pergunta.alternativa3,
            pergunta.alternativa4
        ]
        texto_resposta_correta = alternativas[int(resposta_correta) - 1]
    else:
        pergunta = PerguntaVerdadeiroFalso.objects.filter(id=pergunta_id).first()
        resposta_correta = str(pergunta.resposta)
        texto_resposta_correta = 'Verdadeiro' if pergunta.resposta else 'Falso'

    acertou = (resposta == resposta_correta)
    marcar_pergunta_respondida(request.user, pergunta_id, acertou)
    return JsonResponse({
        'acertou': acertou,
        'resposta_correta': texto_resposta_correta,
        'mensagem': 'Você acertou!' if acertou else 'Você errou.'
    })

@require_POST
def marcar_video_assistido(request, id_video):
    video = get_object_or_404(PlaylistVideo, id=id_video)
    progresso, created = ProgressoVideo.objects.get_or_create(usuario=request.user, playlist_video=video)
    if created:
        progresso.video_completo = True
    else:
        progresso.data_conclusao = timezone.now()
    progresso.save()
    return JsonResponse({"completo": progresso.video_completo})


def verificarConquistaPerguntasRespondidas(usuario):
    CONQUISTAS_RESPOSTAS = {
        1: "Primeira Resposta",
        5: "Respondedor Ávido",
        10: "Especialista nas Respostas",
    }

    perfil = usuario.perfil
    perfil.perguntas_respondidas += 1
    perfil.save()
    
    nome_conquista = CONQUISTAS_RESPOSTAS.get(perfil.perguntas_respondidas)
    if nome_conquista:
        registrar_conquista(usuario, nome_conquista)


def verificarConquistaCursosCriados(usuario):
    CONQUISTAS_CURSOS = {
        1: "Instrutor Inovador",
        3: "Instrutor Nato"
    }

    perfil = usuario.perfil
    perfil.cursos_criados += 1
    perfil.save()

    nome_conquista = CONQUISTAS_CURSOS.get(perfil.cursos_criados)
    if nome_conquista:
        registrar_conquista(usuario, nome_conquista)


def verificarConquistaCursosConcluidos(usuario):
    CONQUISTAS_CURSOS_CLUIDOS = {
        1: "Iniciante Curioso",
        2: "Estudioso Dedicado"
    }

    perfil = usuario.perfil
    perfil.cursos_concluidos += 1
    perfil.save()

    nome_conquista = CONQUISTAS_CURSOS_CLUIDOS.get(perfil.cursos_concluidos)
    if nome_conquista:
        registrar_conquista(usuario, nome_conquista)


def verificarConquistaPerguntasCriadas(usuario):
    CONQUISTAS_PERGUNTAS_CRIADAS = {
        1: "Curioso",
        5: "Investigador Ágil",
    }

    perfil = usuario.perfil
    perfil.perguntas_criadas += 1
    perfil.save()

    nome_conquista = CONQUISTAS_PERGUNTAS_CRIADAS.get(perfil.perguntas_criadas)
    if nome_conquista:
        registrar_conquista(usuario, nome_conquista)

        
def registrar_conquista(usuario, nome_conquista):
    tipo = TipoConquista.objects.get(nome=nome_conquista)
    if not Conquista.objects.filter(tipo=tipo, usuario=usuario).exists():
        Conquista.objects.create(tipo=tipo, usuario=usuario)
        adicionar_xp_perfil(usuario.perfil, tipo.xp)
        

@require_POST
def marcar_perguntas_concluidas(request, id_video):
    video = get_object_or_404(PlaylistVideo, id=id_video)
    progresso = ProgressoVideo.objects.get(usuario=request.user, playlist_video=video)
    progresso.perguntas_respondidas = True    
    progresso.save()
    xp = 20
    adicionar_xp_perfil(request.user.perfil, xp)
    verificarConquistaCursosConcluidos(request.user)
    return JsonResponse({"perguntas_respondidas": progresso.perguntas_respondidas})


def marcar_pergunta_respondida(usuario, pergunta_id, acertou):
    pergunta = get_object_or_404(Pergunta, id=pergunta_id)
    progresso, created = ProgressoPergunta.objects.get_or_create(usuario=usuario, pergunta=pergunta)

    if created:
        progresso.respondida = True
        progresso.data_respondida = timezone.now()
        progresso.resposta_correta = acertou
        progresso.save()
        if acertou:
            adicionar_xp_perfil(usuario.perfil, 10)
            verificarConquistaPerguntasRespondidas(usuario)
    else:
        if not progresso.resposta_correta and acertou:
            progresso.data_respondida = timezone.now()
            progresso.resposta_correta = acertou
            progresso.save()
            
            adicionar_xp_perfil(usuario.perfil, 10)
            verificarConquistaPerguntasRespondidas(usuario)


def adicionar_xp_perfil(perfil, xp):
    perfil.xp += xp
    perfil.save()