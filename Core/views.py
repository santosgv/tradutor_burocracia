from django.shortcuts import render
from openai import OpenAI
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from Core.models import TermoJuridico


def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')


client = OpenAI(api_key=settings.OPENAI_API_KEY)

@login_required
def get_termos_juridicos(request):
    termos = TermoJuridico.objects.filter(usuario=request.user).order_by('-data_busca')[:20]
    data = [{
        'termo_buscado': termo.termo_buscado,
        'traducao': termo.traducao,
        'lei_relacionada': termo.lei_relacionada,
        'tags': termo.tags,
        'data_busca': termo.data_busca.isoformat()
    } for termo in termos]
    return JsonResponse(data, safe=False)

@csrf_exempt
def chat_view(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Explique em linguagem simples para leigos esse trecho juridico. Use no máximo 100 caracteres."},
                {"role": "user", "content": user_message},
            ],
            max_tokens=150
        )
        ai_message = response.choices[0]['text']
        return JsonResponse({'message': ai_message})
    return render(request, 'resultado.html')