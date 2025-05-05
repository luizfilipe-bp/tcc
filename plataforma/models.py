from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator

DIFICULDADE = [
    ('basico', 'Básico'),
    ('intermediario', 'Intermediário'),
    ('avancado', 'Avançado')
]


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    foto_perfil = models.FileField(upload_to='img/perfil', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])], default='img/perfil/default.png')
    xp = models.IntegerField(default=0)
    vida = models.IntegerField(default=10)
    cursos_concluidos = models.IntegerField(default=0)
    cursos_criados = models.IntegerField(default=0)
    perguntas_criadas = models.IntegerField(default=0)
    perguntas_respondidas = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.usuario.username}'


@receiver(post_save, sender=User)
def create_user_profile(instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)


@receiver(post_save, sender=User)
def save_user_profile(instance, **kwargs):
    instance.perfil.save()


class Video(models.Model):
    youtube_id = models.CharField(max_length=11, unique=True)
    #thumbnail = models.FileField(upload_to='uploads/videos/thumbnails', blank=True, null=True, validators = [FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])])
    thumbnail = models.URLField(max_length=200)
    titulo = models.CharField(max_length=150)
    canal = models.CharField(max_length=150)
    # visivel = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.titulo}"
    
    
class Playlist(models.Model):
    nome = models.CharField(max_length=50)
    descricao = models.CharField(max_length=250)
    nivel_dificuldade = models.CharField(max_length=13, choices=DIFICULDADE, default='basico')
    categoria = models.CharField(max_length=40)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):  
        return f"{self.nome} - {self.autor.username}"
    
    
class PlaylistVideo(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    nivel_dificuldade = models.CharField(max_length=13, choices=DIFICULDADE, default='basico')      # dificuldade do video
    # adicionado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('playlist', 'video')  

    def __str__(self):
        return f"{self.video.titulo} - {self.nivel_dificuldade}"


class Pergunta(models.Model):
    pergunta = models.CharField(max_length=250)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    video_pergunta = models.ForeignKey(PlaylistVideo, on_delete=models.CASCADE)
    avaliacao_positiva = models.IntegerField(default=0)
    avaliacao_negativa = models.IntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    nivel_dificuldade = models.CharField(max_length=13, choices=DIFICULDADE, default='basico')

    def __str__(self):
        return f'{self.pergunta} - {self.autor.username} - {self.video_pergunta.video.titulo}'


class PerguntaAlternativas(Pergunta):
    alternativa1 = models.CharField(max_length=100)
    alternativa2 = models.CharField(max_length=100)
    alternativa3 = models.CharField(max_length=100)
    alternativa4 = models.CharField(max_length=100)
    alternativa_correta = models.IntegerField()


class PerguntaVerdadeiroFalso(Pergunta):
    resposta = models.BooleanField()


class ProgressoVideo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist_video = models.ForeignKey(PlaylistVideo, on_delete=models.CASCADE)
    video_completo = models.BooleanField(default=False)  
    perguntas_respondidas = models.BooleanField(default=False)
    data_conclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('usuario', 'playlist_video')

    def __str__(self):
        return f"{self.usuario.username} - {self.playlist_video.video.titulo}"


class ProgressoPergunta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)
    respondida = models.BooleanField(default=False)
    acertou = models.BooleanField(default=False)
    data_respondida = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('usuario', 'pergunta')

    def __str__(self):
        return f"{self.usuario.username} - {self.pergunta.pergunta[:50]}"


class TipoConquista(models.Model):
    nome = models.CharField(max_length=50)
    descricao = models.CharField(max_length=250)
    imagem = models.FileField(upload_to='img/conquistas', blank=True, null=True, validators = [FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])])
    xp = models.IntegerField(default=0)

    def __str__(self):
        return self.nome
    

class Conquista(models.Model):
    tipo = models.ForeignKey(TipoConquista, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_conquista = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo.nome} - {self.usuario.username}"