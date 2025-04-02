from django import forms
from .models import Playlist, DIFICULDADE

class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['nome', 'descricao', 'nivel_dificuldade', 'categoria']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'nome': 'Nome da Playlist',
            'descricao': 'Descrição',
            'nivel_dificuldade': 'Nível de Dificuldade',
            'categoria': 'Categoria',
        }


class PlaylistVideoForm(forms.Form):
    url_video = forms.CharField(label='Link do Vídeo', max_length=50, required=True)
    nivel_dificuldade = forms.ChoiceField(choices=DIFICULDADE, label="Nível de Dificuldade")

    labels = {
        'url_video': 'Link do vídeo',
        'nivel_dificuldade': 'Nível de Dificuldade',
    }
    