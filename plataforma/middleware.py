from django.utils import timezone
from .models import Perfil
from django.shortcuts import get_object_or_404

class VidaMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		user = getattr(request, 'user', None)
		if user and user.is_authenticated:
			perfil = get_object_or_404(Perfil, usuario=request.user)
			perfil.recarregar_vida_por_hora()

		response = self.get_response(request)
		return response
