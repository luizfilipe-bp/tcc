from django import forms
from .models import Playlist, DIFICULDADE, PerguntaAlternativas, PerguntaVerdadeiroFalso

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
    

class PerguntaForm(forms.Form):
    TIPO_PERGUNTA = [
        ('alternativas', 'Alternativas'),
        ('verdadeiro_falso', 'Verdadeiro ou Falso'),
    ]
    
    tipo_pergunta = forms.ChoiceField(choices=TIPO_PERGUNTA, label="Tipo de Pergunta")
    pergunta = forms.CharField(max_length=250, label="Texto da Pergunta")
    
    alternativa1 = forms.CharField(max_length=100, required=False, label="Alternativa 1")
    alternativa2 = forms.CharField(max_length=100, required=False, label="Alternativa 2")
    alternativa3 = forms.CharField(max_length=100, required=False, label="Alternativa 3")
    alternativa4 = forms.CharField(max_length=100, required=False, label="Alternativa 4")
    alternativa_correta = forms.IntegerField(
        required=False,
        label="Alternativa Correta (1 a 4)",
        min_value=1,
        max_value=4
    )
    resposta = forms.BooleanField(required=False, label="Resposta (Verdadeiro/Falso)")

    def clean(self):
        cleaned_data = super().clean()
        tipo_pergunta = cleaned_data.get('tipo_pergunta')

        if tipo_pergunta == 'alternativas':
            for i in range(1, 5):
                if not cleaned_data.get(f'alternativa{i}'):
                    self.add_error(f'alternativa{i}', 'Este campo é obrigatório para perguntas de alternativas.')
            if not cleaned_data.get('alternativa_correta'):
                self.add_error('alternativa_correta', 'Este campo é obrigatório para perguntas de alternativas.')
        elif tipo_pergunta == 'verdadeiro_falso':
            for i in range(1, 5):
                cleaned_data[f'alternativa{i}'] = None
            cleaned_data['alternativa_correta'] = None
            if cleaned_data.get('resposta') is None:
                self.add_error('resposta', 'Este campo é obrigatório para perguntas de verdadeiro ou falso.')

        return cleaned_data