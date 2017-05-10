from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import logout, user_logged_in


def login(request):
    return render (request,'account/login.html')


def menu(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    # Recupera o nome do usuário logado no sistema
    # usuario = User.objects.filter(username=request.user).values("username","first_name")
    # Cria um objeto do tipo 'context' => context = {'username': ''}
    # context = usuario.get()

    title_page = "Principal - Easy Lawyer"
    context = {
        'user_name': request.user,
        'title_page': title_page
    }
    return render(request,'core/home.html',context)


def logout_user(request):

    # Faz o logout do usuário contido na requisição, limpando todos os dados da sessão corrente;
    logout(request)
    # Redireciona para a página de login
    return HttpResponseRedirect('/')


# Create your views here.
