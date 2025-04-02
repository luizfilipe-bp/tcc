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


@receiver(post_save, sender=User)
def create_user_profile(instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)


@receiver(post_save, sender=User)
def save_user_profile(instance, **kwargs):
    instance.perfil.save()


class Video(models.Model):
    youtube_id = models.CharField(max_length=11, unique=True)
    thumbnail = models.FileField(upload_to='uploads/videos/thumbnails', blank=True, null=True, validators = [FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])])
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
    videos = models.ManyToManyField(Video, blank=True)

    def __str__(self):  
        return f"{self.nome} - {self.autor.username}"
    
    
class PlaylistVideo(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    nivel_dificuldade = models.CharField(max_length=13, choices=DIFICULDADE, default='basico')
    # adicionado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('playlist', 'video')  

    def __str__(self):
        return f"{self.video.titulo} - {self.nivel_dificuldade}"




'''
class Pergunta(models.Model):
    pergunta = models.CharField(max_length=250)
    autor = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    video_pergunta = models.ForeignKey(Video, on_delete=models.CASCADE)
    avaliacao_positiva = models.IntegerField(default=0)
    avaliacao_negativa = models.IntegerField(default=0)


class PerguntaAlternativas(Pergunta):
    alternativa1 = models.CharField(max_length=100)
    alternativa2 = models.CharField(max_length=100)
    alternativa3 = models.CharField(max_length=100)
    alternativa4 = models.CharField(max_length=100)
    alternativa_correta = models.IntegerField()


class PerguntaVerdadeiroFalso(Pergunta):
    resposta = models.BooleanField()

    
'''