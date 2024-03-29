from django.shortcuts import render, redirect
from django.http import HttpResponse
from .utils import calcula_total, calcula_equilibrio_financeiro, organizar_contas
from .models import Conta, Categoria
from extrato.models import Valores
from datetime import datetime
from django.contrib.messages import constants
from django.contrib import messages

# Create your views here.

def home(request):
    valores = Valores.objects.filter(data__month=datetime.now().month)
    entradas = valores.filter(tipo='E')
    saidas = valores.filter(tipo='S')

    total_entradas = calcula_total(entradas, 'valor')
    total_saidas = calcula_total(saidas, 'valor')

    contas = Conta.objects.all()
    total_contas = 0
    for conta in contas:
        total_contas += conta.valor

    percentual_gastos_essenciais, percentual_gastos_nao_essenciais = calcula_equilibrio_financeiro()

    contas_vencidas, contas_proximas_vencimento, restantes = organizar_contas()

    contas_vencidas = calcula_total(contas_vencidas, 'valor')
    contas_proximas_vencimento = calcula_total(contas_proximas_vencimento, 'valor')

    return render(request, 'home.html', {'contas': contas, 'total_contas':total_contas, 'total_entradas': total_entradas, 'total_saidas': total_saidas, 'percentual_gastos_essenciais': int(percentual_gastos_essenciais), 'percentual_gastos_nao_essenciais': int(percentual_gastos_nao_essenciais), 'contas_vencidas': contas_vencidas, 'contas_proximas_vencimento': contas_proximas_vencimento})

def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    total_contas = 0
    for conta in contas:
        total_contas += conta.valor
    return render(request, 'gerenciar.html',{'contas': contas, 'total_contas': total_contas, 'categorias':categorias})

def cadastrar_banco(request):
    apelido = request.POST.get('apelido')
    banco = request.POST.get('banco')
    tipo = request.POST.get('tipo')
    valor = request.POST.get('valor')
    icone = request.FILES.get('icone')
    
    if len(apelido.strip()) == 0 or len(valor.strip()) == 0:
        messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
        return redirect('/perfil/gerenciar/')

    #TODO: Realizar validações.(Pesquisar sobre Regex)

    conta = Conta(
        apelido=apelido,
        banco=banco,
        tipo=tipo,
        valor=valor,
        icone=icone
    )

    # Salva os dados no banco.
    conta.save()

    messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso!')
    return redirect('/perfil/gerenciar/')

def deletar_banco(request, id):
    conta = Conta.objects.get(id=id)
    conta.delete()

    messages.add_message(request, constants.SUCCESS, 'Conta deletada com sucesso!')
    return redirect('/perfil/gerenciar/')

def cadastrar_categoria(request):
    nome = request.POST.get('categoria')
    essencial = bool(request.POST.get('essencial'))

    #TODO: Realizar validações.(Pesquisar sobre Regex)

    categoria = Categoria(
        categoria=nome,
        essencial=essencial
    )

    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')

def update_categoria(request, id):
    categoria = Categoria.objects.get(id=id)

    categoria.essencial = not categoria.essencial

    categoria.save()

    return redirect('/perfil/gerenciar/')

def dashboard(request):
    dados = {}

    categorias = Categoria.objects.all()

    for categoria in categorias:
        total = 0
        valores = Valores.objects.filter(categoria=categoria)
        for v in valores:
            total = total + v.valor
        
        dados[categoria.categoria] = total
    return render(request, 'dashboard.html', {'labels': list(dados.keys()), 'values': list(dados.values())})