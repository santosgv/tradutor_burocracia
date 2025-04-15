from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.messages import constants
from .models import Usuario
from django.contrib import auth
import re


def validar_senha_forte(senha):
    """
    Valida se a senha atende aos requisitos:
    - Mínimo 6 caracteres
    - Pelo menos 1 letra maiúscula
    - Pelo menos 1 caractere especial
    """
    if len(senha) < 6:
        return False, "A senha deve ter pelo menos 6 caracteres"
    
    if not re.search(r'[A-Z]', senha):
        return False, "A senha deve conter pelo menos 1 letra maiúscula"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
        return False, "A senha deve conter pelo menos 1 caractere especial"
    
    return True, ""

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
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirm-password')
        interesses = request.POST.getlist('temas_interesse')

        if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas não coincidem')
            return redirect('/auth/cadastrar')

        if len(first_name.strip()) == 0 or len(senha.strip()) == 0:
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect('/auth/cadastrar')
        
        senha_valida, msg_erro = validar_senha_forte(senha)
        if not senha_valida:
            messages.add_message(request, constants.ERROR, msg_erro)
            return redirect('/auth/cadastrar')

        
        user = Usuario.objects.filter(email=email)
        
        if user.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um usário com esse username')
            return redirect('/auth/cadastrar')
        
        try:
            Usuario.objects.create_user(
                                            username=first_name,
                                            data_nascimento=data_nascimento,
                                            cpf=cpf,
                                            temas_interesse=interesses,
                                            email = email,
                                            telefone=telefone,
                                            password=senha)
            

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

from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        # Adicione lógica personalizada aqui se necessário
        return super().form_valid(form)