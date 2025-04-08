from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.messages import constants
from .models import Usuario
from django.contrib import auth

def cadastrar(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'cadastrar.html')
        
    elif request.method == "POST":
        first_name = request.POST.get('first_name')
        cpf = request.POST.get('cpf')
        data_nascimento = request.POST.get('data_nascimento')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        senha = request.POST.get('password')
        confirmar_senha = request.POST.get('confirm-password')
        interesses = request.POST.getlist('temas_interesse')

        print(first_name, cpf, data_nascimento, email, telefone, senha, confirmar_senha, interesses)

        

        if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas não coincidem')
            return redirect('/auth/cadastrar')

        if len(first_name.strip()) == 0 or len(senha.strip()) == 0:
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect('/auth/cadastrar')
        
        user = Usuario.objects.filter(email=email)
        
        if user.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um usário com esse username')
            return redirect('/auth/cadastrar')
        
        try:
            user = Usuario.objects.create_user(
                                            username=first_name,
                                            data_nascimento=data_nascimento,
                                            cpf=cpf,
                                            temas_interesse=interesses,
                                            email = email,
                                            telefone=telefone,
                                            password=senha)
            user.save()

            messages.add_message(request, constants.SUCCESS, 'Foi Enviado Para seu email o Link de ativaçao da sua conta')
            return redirect('/auth/logar')
        except Exception as msg:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema')
            print(msg)
            return redirect('/auth/cadastrar')

def logar(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('chat_view')
        return render(request, 'logar.html')
    elif request.method == "POST":
        email = request.POST.get('email')
        senha = request.POST.get('password')

        usuario = auth.authenticate(email=email, password=senha)


        if not usuario:
            messages.add_message(request, constants.ERROR, 'Username ou senha inválidos')
            return redirect('/auth/logar')
        else:
            auth.login(request, usuario)
            return redirect('chat_view')

def sair(request):
    auth.logout(request)
    return redirect('/auth/logar')