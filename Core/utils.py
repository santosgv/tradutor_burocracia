from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from openai import OpenAI

from Autenticacao.models import HistoricoConsumo, Usuario,SaldoCredito
from .models import TermoJuridico
from datetime import datetime
import random

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class MockOpenAIResponse:
    def __init__(self):
        self.choices = [self._generate_random_choice()]
        self.created = int(datetime.now().timestamp())
        self.model = "gpt-3.5-turbo"
        self.usage = {
            "prompt_tokens": random.randint(50, 120),
            "completion_tokens": random.randint(30, 90),
            "total_tokens": random.randint(80, 210)
        }
    
    def _generate_random_choice(self):
        termos_juridicos = {
            "Habeas corpus": "É um direito que protege a liberdade de locomoção quando alguém sofre ou está ameaçado de sofrer violência ou coação em sua liberdade de ir e vir.",
            "Usucapião": "Modo de adquirir propriedade através da posse prolongada e ininterrupta de um bem, com duração variável conforme o caso (5 a 15 anos).",
            "Alienação fiduciária": "Garantia real onde o devedor transfere ao credor a propriedade resolúvel de um bem, até que a dívida seja quitada.",
            "Ação rescisória": "Recurso que busca anular uma decisão judicial transitada em julgado, por vícios como erro grosseiro ou fraude processual.",
            "Arrolamento de bens": "Inventário simplificado para heranças de pequeno valor ou quando não há imóveis envolvidos."
        }
        
        temas = [
            "direito civil",
            "direito penal",
            "direito trabalhista",
            "direito tributário",
            "direito previdenciário"
        ]
        
        padroes_resposta = [
            "Em linguagem simples, {termo} significa: {explicacao}",
            "Você quer saber sobre {termo}. Basicamente: {explicacao}",
            "{termo} é um termo jurídico que se refere a: {explicacao}",
            "Na prática, {termo} quer dizer que: {explicacao}",
            "Traduzindo para o português claro: {termo} = {explicacao}"
        ]
        
        termo, explicacao = random.choice(list(termos_juridicos.items()))
        template = random.choice(padroes_resposta)
        
        return {
            "message": {
                "content": template.format(termo=termo, explicacao=explicacao),
                "role": "assistant"
            },
            "finish_reason": "stop",
            "index": 0,
            "metadata": {
                "tema": random.choice(temas),
                "complexidade": random.choice(["baixa", "média", "alta"]),
                "fontes": [
                    f"Art. {random.randint(1, 1000)} do Código Civil",
                    f"Lei {random.randint(5_000, 15_000)}/{random.randint(1990, 2023)}"
                ]
            }
        }
    
    @property
    def text(self):
        return self.choices[0]['message']['content']

def mock_openai_completion_create(*args, **kwargs):
    return MockOpenAIResponse()

@csrf_exempt
def chat_view_teste(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        saldo = SaldoCredito.objects.filter(usuario=request.user).first()


    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not saldo or saldo.creditos < 1:
            return JsonResponse({
                'status': 'error',
                'message': 'Créditos insuficientes, Faça uma nova recarga de créditos.'
            }, status=402)

        
        termo_existente = TermoJuridico.objects.filter(
            usuario=request.user,
            termo_buscado__icontains=user_message  # busca exata ignorando case
        ).first()

        if termo_existente:
            return JsonResponse({'message': termo_existente.traducao})
        


        response = client.chat.completions.create = mock_openai_completion_create(
            engine="text-davinci-003",
            messages=[
                {"role": "system", "content": "Explique em linguagem simples para leigos esse trecho juridico. Use no máximo 100 caracteres."},
                {"role": "user", "content": user_message},
            ],
            max_tokens=150
        )

        
        ai_message = response.text

        saldo.consumir_credito(1)

        pesquisa = TermoJuridico.objects.create(
            usuario=request.user,
            termo_buscado=user_message,
            traducao=response.text,
            lei_relacionada=", ".join(response.choices[0]['metadata']['fontes']),
            tags=response.choices[0]['metadata']['tema']
        )
        pesquisa.save()
        atualiza = Usuario.objects.get(id=request.user.id)
        atualiza.ultima_busca = datetime.now()
        atualiza.save()

        HistoricoConsumo.objects.create(
        usuario=request.user,
        termo=user_message,
        creditos_usados=1
        )
        print(saldo.creditos)
        return JsonResponse({'message': ai_message,
                             'novo_saldo': saldo.creditos})
    return render(request, 'resultado.html')