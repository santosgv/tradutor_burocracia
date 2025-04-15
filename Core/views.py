from django.shortcuts import redirect, render
from openai import OpenAI
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import  HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from Autenticacao.models import  SaldoCredito, Usuario,Creditos
from Core.models import TermoJuridico
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

PLANOS = {
        10: {'preco': 9.90, 'creditos': 10, 'descricao': '10 créditos'},
        30: {'preco': 19.90, 'creditos': 30, 'descricao': '30 créditos (Mais Popular)'},
        100: {'preco': 49.90, 'creditos': 100, 'descricao': '100 créditos (Melhor Oferta)'}
    }

def index(request):
    if not request.user.is_authenticated:
        return render(request, 'index.html')
    saldo = SaldoCredito.objects.filter(usuario=request.user).first()
    return render(request, 'index.html', {'saldo': saldo.creditos})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')


client = OpenAI(api_key=settings.OPENAI_API_KEY)

@login_required(login_url='/auth/logar/')
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


@login_required(login_url='/auth/logar/')
@csrf_exempt
def chat_view(request):
    saldo = SaldoCredito.objects.filter(usuario=request.user).first()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not saldo or saldo.creditos < 1:
            return JsonResponse({
                'status': 'error',
                'message': 'Créditos insuficientes, Faça uma nova recarga de créditos.'
            }, status=402)

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

        saldo.consumir_credito(1)

        return JsonResponse({'message': ai_message,
                             'novo_saldo': saldo.creditos})
    return render(request, 'resultado.html',{'saldo': saldo.creditos})

@login_required(login_url='/auth/logar/')
def creditos(request):
    return render(request, 'vendas.html',{"planos": PLANOS,})

@login_required(login_url='/auth/logar/')
def criar_checkout(request, plano):
    if plano not in PLANOS:
        return redirect('pagamento-erro')

    package = PLANOS[plano]

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'brl',
                'product_data': {
                    'name': f"{package['descricao']}",
                },
                'unit_amount': int(package['preco']* 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/checkout/sucesso/') + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri('/checkout/erro/'),
        metadata={
            'user_id': request.user.id,
            'creditos': package['creditos']
        }
    )


    return redirect(session.url, code=303)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Processar pagamento
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        creditos = int(session['metadata']['creditos'])

        user = Usuario.objects.get(id=user_id)
        saldo, created = SaldoCredito.objects.get_or_create(usuario=user)
        saldo.creditos += creditos
        saldo.save()

    return HttpResponse(status=200)

@login_required(login_url='/auth/logar/')
def pagamento_sucesso(request):
    session_id = request.GET.get('session_id')
    
    if not session_id:
        return redirect('pagamento-erro')
    
    try:
        # Recupera a sessão do Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Verifica se a sessão pertence ao usuário atual
        if str(session.metadata.get('user_id')) != str(request.user.id):
            return redirect('pagamento-erro')
        
        # Verifica o status do pagamento
        if session.payment_status == 'paid':
            creditos = int(session.metadata.get('creditos'))
            

            usuario = SaldoCredito.objects.get(usuario=request.user.id)
            usuario.creditos += creditos
            usuario.save()

            Creditos.objects.create(
                usuario=request.user,
                quantidade=creditos,
                valor=PLANOS[creditos]['preco'] if creditos in PLANOS else 0,
                payment_id=session.payment_intent,
                status='pago'
            )
            
            context = {
                'quantidade_creditos': creditos,
                'valor': PLANOS[creditos]['preco'] if creditos in PLANOS else 0,
                'data': session.created,
                'payment_id': session.payment_intent
            }
            
            return render(request, 'sucesso.html', context)
    
    except stripe.error.InvalidRequestError as e:
        print(f"Sessão não encontrada: {e}")
    except Exception as e:
        print(f"Erro ao verificar pagamento: {e}")
    
    return redirect('pagamento-erro')

@login_required(login_url='/auth/logar/')
def checkout_erro(request):
    return render(request, 'erro.html')