from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
import urllib.parse as urlparse
from .forms import PlaylistForm, PlaylistVideoForm, PerguntaForm, FormularioRespostaAlternativa, FormularioRespostaVerdadeiroFalso
from django.contrib.auth.decorators import login_required
from .models import Playlist, Video, PlaylistVideo, Pergunta, PerguntaAlternativas, PerguntaVerdadeiroFalso, ProgressoVideo, ProgressoPergunta, TipoConquista, Conquista, Perfil, ProgressoPlaylist
from dotenv import load_dotenv
from django.http import JsonResponse
import os
import requests
from django.views.decorators.http import require_POST
from django.db.models import Sum


@login_required(login_url='/auth/login')
def principal(request):
    playlists = Playlist.objects.all()
    playlists = playlists.filter(playlistvideo__isnull=False).distinct()
    playlists = playlists.prefetch_related('playlistvideo_set__video')

    return render(request, 'principal.html', {'playlists': playlists})

@login_required(login_url='/auth/login')
def perfil(request):
    perfil = get_object_or_404(Perfil, usuario=request.user)
    conquistas = Conquista.objects.filter(usuario=request.user).order_by('-data_conquista')
    reputacao = get_reputacao(request)
    context = {
        'perfil': perfil,
        'conquistas': conquistas,
        'reputacao': reputacao
    }
    return render(request, 'perfil.html', context)


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
            'nivel_dificuldade': pergunta.get_nivel_dificuldade_display(),
            'pergunta': pergunta.pergunta,
            'alternativas': [pergunta.alternativa1, pergunta.alternativa2, pergunta.alternativa3, pergunta.alternativa4],
            'alternativa_correta': pergunta.alternativa_correta
        })
    for pergunta in perguntas_vf:
        perguntas.append({
            'id': pergunta.id,
            'tipo': 'verdadeiro_falso',
            'nivel_dificuldade': pergunta.get_nivel_dificuldade_display(),
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


def get_progresso_playlist(usuario, playlist_videos):
    progresso_videos = ProgressoVideo.objects.filter(usuario=usuario, playlist_video__in=playlist_videos)

    somatorio_videos_completos = progresso_videos.filter(video_completo=True, perguntas_respondidas=True).count()
    total = playlist_videos.count()

    if total == 0:
        return 0
    porcentagem_progresso = (somatorio_videos_completos / total) * 100
    print(f"Somatório: {somatorio_videos_completos}, Total: {total}, Porcentagem: {porcentagem_progresso}")
    return int(round(porcentagem_progresso))


def finalizar_playlist(request, id):
    playlist = get_object_or_404(Playlist, id=id)
    playlist_videos = PlaylistVideo.objects.filter(playlist=playlist)
    
    progresso_playlist = get_progresso_playlist(request.user, playlist_videos)
    if progresso_playlist == 100:
        xp = 0
        progresso_playlist = get_object_or_404(ProgressoPlaylist, usuario=request.user, playlist=playlist)
        if progresso_playlist.playlist_completa is False:
            xp = 200
            progresso_playlist = ProgressoPlaylist.objects.get(usuario=request.user, playlist=playlist)
            progresso_playlist.playlist_completa = True
            progresso_playlist.data_conclusao = timezone.now()
            progresso_playlist.save()
            verificarConquistaCursosConcluidos(request.user)
            adicionar_xp_perfil(request.user.perfil, xp)
    else:
        return redirect('assistir_playlist', id=id, index_video=0)
    
    context = {
        'playlist': playlist,
        'xp': xp,
    }
    return render(request, 'finalizar_playlist.html', context)

def get_videos_liberados(playlist_videos, usuario):     
    progresso_videos = ProgressoVideo.objects.filter(
        usuario=usuario,
        playlist_video__in=playlist_videos
    )
    videos_liberados = {p.playlist_video_id for p in progresso_videos}
    return videos_liberados

def iniciar_progresso_video(usuario, playlist_video):
    progresso_video, created = ProgressoVideo.objects.get_or_create(
        usuario=usuario,
        playlist_video=playlist_video,
        defaults={
            'video_completo': False,
            'perguntas_respondidas': False,
            'data_conclusao': None
        }
    )
    if created:
        progresso_video.save()
    
@login_required
def assistir_playlist(request, id, index_video=0):
    playlist = get_object_or_404(Playlist, id=id)
    playlist_videos = PlaylistVideo.objects.filter(playlist=playlist)

    if index_video == 0:
        ProgressoPlaylist.objects.get_or_create(usuario=request.user, playlist=playlist)

    videos_liberados = get_videos_liberados(playlist_videos, request.user)
    if index_video < 0 or index_video >= len(playlist_videos) or index_video > len(videos_liberados):
        return redirect('assistir_playlist', id=id, index_video=0)
    
    iniciar_progresso_video(request.user, playlist_video=playlist_videos[index_video])
    videos_liberados.add(playlist_videos[index_video].id)
    video_atual = playlist_videos[index_video]

    context = {
        'playlist': playlist,
        'playlist_videos': playlist_videos,
        'video_atual': video_atual, 
        'index_video': index_video,
        'videos_liberados': videos_liberados,
        'perfil': request.user.perfil
    }
    return render(request, 'assistir_playlist.html', context)


@login_required(login_url="/auth/login")
@require_POST
def retirar_vida(request):
    perfil = request.user.perfil
    
    if perfil.vida > 0:
        perfil.vida -= 1
        perfil.save()
        status = 'sucesso'
        vidas = perfil.vida
    else:
        status = 'erro'
        vidas = 0

    return JsonResponse({
        'status': status,
        'vidas': vidas,
    })


def obter_pergunta_e_resposta_correta(pergunta_id): 
    try:
        pergunta = PerguntaAlternativas.objects.get(id=pergunta_id)
        indice = int(pergunta.alternativa_correta) - 1
        texto_alternativa_correta = [
            pergunta.alternativa1,
            pergunta.alternativa2,
            pergunta.alternativa3,
            pergunta.alternativa4,
        ][indice]
        alternativa_correta = str(pergunta.alternativa_correta)
    except PerguntaAlternativas.DoesNotExist:
        pergunta = get_object_or_404(PerguntaVerdadeiroFalso, id=pergunta_id)
        alternativa_correta = 'True' if pergunta.resposta else 'False'
        texto_alternativa_correta = 'Verdadeiro' if pergunta.resposta else 'Falso'
    return pergunta, alternativa_correta, texto_alternativa_correta

def checar_resposta(request):
    XP_POR_NIVEL = {
        'basico': 10,
        'intermediario': 20,
        'avancado': 30,
    }   
    pergunta_id = request.POST.get('pergunta_id')
    resposta_cliente = request.POST.get('resposta')

    pergunta, alternativa_correta, texto_alternativa_correta = obter_pergunta_e_resposta_correta(pergunta_id)

    acertou = (resposta_cliente == alternativa_correta)
    if acertou:
        novo_acerto = marcar_pergunta_respondida(request.user, pergunta, acertou)
        if novo_acerto:
            xp = XP_POR_NIVEL.get(pergunta.nivel_dificuldade)
            adicionar_xp_perfil(request.user.perfil, xp)
            verificarConquistaPerguntasRespondidas(request.user)

    return JsonResponse({
        'acertou': acertou,
        'texto_alternativa_correta': texto_alternativa_correta,
        'xp': XP_POR_NIVEL.get(pergunta.nivel_dificuldade),
        'mensagem': 'Você acertou!' if acertou else 'Você errou.'
    })

def marcar_pergunta_respondida(usuario, pergunta, acertou):
    progresso, criado = ProgressoPergunta.objects.get_or_create(
        usuario=usuario,
        pergunta=pergunta,
        defaults={
            'respondida': True,
            'data_respondida': timezone.now(),
            'acertou': acertou,
        }
    )

    novo_acerto = False
    if not criado and not progresso.acertou and acertou:
        progresso.acertou = True
        progresso.data_respondida = timezone.now()
        progresso.save(update_fields=['acertou', 'data_respondida'])
        novo_acerto = True

    if criado and acertou:
        novo_acerto = True

    return novo_acerto

def marcar_todas_perguntas_respondidas(request, id_video):
    progressoVideo = get_object_or_404(ProgressoVideo, usuario=request.user, playlist_video=id_video)
    progressoVideo.perguntas_respondidas = True
    progressoVideo.data_conclusao = timezone.now()
    progressoVideo.save()

    return JsonResponse({
        'status': 'sucesso',
        'mensagem': 'Perguntas marcadas como respondidas'
    })


def adicionar_xp_perfil(perfil, xp):
    perfil.xp += xp
    perfil.save()


@require_POST
def marcar_video_assistido(request, id_video):
    video = get_object_or_404(PlaylistVideo, id=id_video)
    progresso = ProgressoVideo.objects.get(usuario=request.user, playlist_video=video)
    progresso.video_completo = True
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
        

def get_reputacao(request):
    usuario = request.user
    perguntas = Pergunta.objects.filter(autor=usuario)

    somatorio_avaliacao_positiva = perguntas.aggregate(Sum('avaliacao_positiva'))['avaliacao_positiva__sum'] or 0
    somatorio_avaliacao_negativa = perguntas.aggregate(Sum('avaliacao_negativa'))['avaliacao_negativa__sum'] or 0
    total = somatorio_avaliacao_positiva + somatorio_avaliacao_negativa

    if total == 0:
        reputacao = 0
    else:
        reputacao = (somatorio_avaliacao_positiva / total) * 100
    return round(reputacao)

