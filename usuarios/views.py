from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth import login as login_django
from django.contrib.auth import logout as logout_django
from django.contrib.auth.models import User


def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    else:
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')
        user = authenticate(username=usuario, password=senha)
        if user:
            login_django(request, user)
            return redirect('principal')
        else:
            messages.error(request, 'Usuário ou senha inválidos. Tente novamente.')
            return render(request, 'login.html')
        
def logout(request):
    logout_django(request)
    return render(request, 'login.html')


def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    else:
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        
        user = User.objects.filter(username=usuario).first()
        if user:
            messages.error(request, 'Já existe um usuário com esse nome. Tente novamente.')
            return redirect('cadastro')

        user = User.objects.create_user(username=usuario, email=email, password=senha)
        user.save()
        
        return render(request, 'login.html')