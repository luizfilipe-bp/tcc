from django import forms
from .models import Playlist, DIFICULDADE, PerguntaAlternativas, PerguntaVerdadeiroFalso

class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['nome', 'descricao', 'nivel_dificuldade', 'categoria']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'maxlength': 250}),
            'nivel_dificuldade': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 40}),
        }
        labels = {
            'nome': 'Nome do curso',
            'descricao': 'Descrição',
            'nivel_dificuldade': 'Nível de Dificuldade',
            'categoria': 'Categoria',
        }


class PlaylistVideoForm(forms.Form):
    url_video = forms.CharField(
        label='Link do Vídeo',
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_dificuldade = forms.ChoiceField(
        choices=DIFICULDADE,
        label="Nível de Dificuldade",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    labels = {
        'url_video': 'Link do vídeo',
        'nivel_dificuldade': 'Nível de Dificuldade',
    }
    
class PerguntaForm(forms.Form):
    TIPO_PERGUNTA = [
        ('alternativas', 'Alternativas'),
        ('verdadeiro_falso', 'Verdadeiro ou Falso'),
    ]
    
    tipo_pergunta = forms.ChoiceField(
        choices=TIPO_PERGUNTA,
        label="Tipo de Pergunta",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    pergunta = forms.CharField(
        max_length=250,
        label="Texto da Pergunta",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    alternativa1 = forms.CharField(
        max_length=100,
        required=False,
        label="Alternativa 1",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    alternativa2 = forms.CharField(
        max_length=100,
        required=False,
        label="Alternativa 2",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    alternativa3 = forms.CharField(
        max_length=100,
        required=False,
        label="Alternativa 3",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    alternativa4 = forms.CharField(
        max_length=100,
        required=False,
        label="Alternativa 4",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_dificuldade = forms.ChoiceField(
        choices=DIFICULDADE,
        label="Nível de Dificuldade",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    alternativa_correta = forms.IntegerField(
        required=False,
        label="Alternativa Correta (1 a 4)",
        min_value=1,
        max_value=4,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    resposta = forms.BooleanField(
        required=False,
        label="Ao marcar o campo a resposta correta será 'Verdadeira'. Deixar desmarcado para 'Falso'.",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

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


class FormularioRespostaPergunta(forms.Form):
	pergunta_id = forms.IntegerField(widget=forms.HiddenInput())
	resposta = forms.ChoiceField(
		widget=forms.RadioSelect(attrs={'class': 'custom-radio'}),
		choices=(),  
		label=""    
	)
     
	def __init__(self, *args, pergunta=None, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['pergunta_id'].initial = pergunta.id

		if isinstance(pergunta, PerguntaAlternativas):
			alternativas = [
				pergunta.alternativa1,
				pergunta.alternativa2,
				pergunta.alternativa3,
				pergunta.alternativa4,
			]
			self.fields['resposta'].choices = [
				(str(i + 1), alt) for i, alt in enumerate(alternativas)
			]
			self.fields['resposta'].label = "Escolha uma alternativa"
		else:
			self.fields['resposta'].choices = [
				('True', 'Verdadeiro'),
				('False', 'Falso'),
			]
			self.fields['resposta'].label = "Selecione Verdadeiro ou Falso"
