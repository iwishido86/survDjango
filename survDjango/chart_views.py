import logging
from datetime import timezone
from random import random, randint

from astropy.io.votable.converters import Int
from django.db.models import Q, Max, Count, Sum, Avg
from django.db.models.functions import Substr
from django.forms import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import render
from plotly.offline import plot
from plotly.graph_objs import Scatter
import FinanceDataReader as fdr
import pandas as pd
from django.utils import timezone

import datetime
from .candle_func import update_anal_candle, create_anal_candle
from .forms import UserLoginForm, SurvForm
from .models import SurvM, QuestionM, AnsM, ResultHstoryL, ResultM, ResultCommentL, SymbolM, CandleL, SimCandleL, \
    AnalDateM, SimContentL, RecoSymbolL, RecoCandleL

from .serializers import RegistrationUserSerializer

logger = logging.getLogger(__name__)


#http://127.0.0.1:8000/chart/
def chart_index_view(request):
    template_name = 'survDjango/chart_index.html'

    analDateM = get_object_or_404(AnalDateM)

    dict_symbollist = []

    if request.method == 'POST':
        serchInput = request.POST.get('serchInput', '')
        symbolMlist = SymbolM.objects.filter(Q(Name__icontains=serchInput) or Q(Symbol__icontains=serchInput))[0:10]

        if symbolMlist.count() == 1:
            return HttpResponseRedirect('/chart/disp/' + symbolMlist[0].SysMarketCd + '/' + symbolMlist[0].Symbol )
        set_symbol= {}

        for symbolM in symbolMlist:
            set_symbol = symbolM.__dict__
            dict_symbollist.append(set_symbol)


    queryday = analDateM.AnalDate - datetime.timedelta(days=10)

    recoSymbolLlist = RecoSymbolL.objects.filter(AnalDate__gte=queryday, RecoDispYn='Y').order_by('-AnalDate')

    dict_recolist = []
    set_reco = {}

    for recoSymbolL in recoSymbolLlist:

        set_reco = recoSymbolL.__dict__
        sim_symbolM = get_object_or_404(SymbolM, SysMarketCd='KRX', Symbol=recoSymbolL.Symbol)
        set_reco['Name'] = sim_symbolM.Name
        set_reco['Prorate'] = (recoSymbolL.NowClose - recoSymbolL.Close) * 100 / recoSymbolL.Close
        dict_recolist.append(set_reco)

    logger.debug(dict_symbollist)

    context = {
        'dict_recolist': dict_recolist,
        'analdate': analDateM.AnalDate,
        'symbollist': dict_symbollist,
    }

    return render(request, template_name, context)


#http://127.0.0.1:8000/chart/admin
def chart_index_admin_view(request):
    template_name = 'survDjango/chart_index_admin.html'

    analDateM = get_object_or_404(AnalDateM)

    dict_symbollist = []

    if request.method == 'POST':
        serchInput = request.POST.get('serchInput', '')
        symbolMlist = SymbolM.objects.filter(Q(Name__icontains=serchInput) or Q(Symbol__icontains=serchInput))[0:10]

        if symbolMlist.count() == 1:
            return HttpResponseRedirect('/chart/disp/' + symbolMlist[0].SysMarketCd + '/' + symbolMlist[0].Symbol )
        set_symbol= {}

        for symbolM in symbolMlist:
            set_symbol = symbolM.__dict__
            dict_symbollist.append(set_symbol)


    queryday = analDateM.AnalDate - datetime.timedelta(days=10)

    recoSymbolLlist = RecoSymbolL.objects.filter(AnalDate__gte=queryday).order_by('-AnalDate')

    dict_recolist = []
    set_reco = {}

    for recoSymbolL in recoSymbolLlist:

        set_reco = recoSymbolL.__dict__
        sim_symbolM = get_object_or_404(SymbolM, SysMarketCd='KRX', Symbol=recoSymbolL.Symbol)
        set_reco['Name'] = sim_symbolM.Name
        set_reco['Prorate'] = (recoSymbolL.NowClose - recoSymbolL.Close) * 100 / recoSymbolL.Close
        dict_recolist.append(set_reco)

    logger.debug(dict_symbollist)

    context = {
        'dict_recolist': dict_recolist,
        'analdate': analDateM.AnalDate,
        'symbollist': dict_symbollist,
    }

    return render(request, template_name, context)


#http://127.0.0.1:8000/symbol/reco/KRX/256840
def chart_reco_view(request,sysmarketcd,symbol):
    template_name = 'survDjango/chart_reco.html'

    symbolM = get_object_or_404(SymbolM, SysMarketCd=sysmarketcd,Symbol=symbol)

    # from django.utils import timezone
    #
    # current_tz = timezone.get_current_timezone()
    # dt_analdate = current_tz.localize(pd.to_datetime(analDateM.AnalDate))
    #
    # logger.debug((dt_analdate)
    recoSymbolL = RecoSymbolL.objects.filter(Symbol=symbol).order_by('-AnalDate')[0]
    logger.debug(recoSymbolL)
    queryday=recoSymbolL.AnalDate - datetime.timedelta(days=20)

    candlelist = CandleL.objects.filter(Symbol=symbolM.Symbol, BaseDate__gte=queryday ,BaseDate__lte=recoSymbolL.AnalDate).order_by('BaseDate')

    candlelist = candlelist[candlelist.count()-10:candlelist.count()]

    now_candle = candlelist[candlelist.count()-1]

    x_data = [x for x in range(0, 19)]

    graph= []
    y_data = []
    list_marker_color = ['gray', 'blue', 'green', 'purple', 'pink', 'navy']
    list_marker_color_index = 0
    for candle in candlelist:
        y_data.append(candle.Close)

    graph.append(Scatter(x=x_data, y=y_data,
            mode='lines', name=symbolM.Name,
            opacity=0.8, marker_color='red'))

    if recoSymbolL.RecoTypeCd == '01':
        reco_candlelist = RecoCandleL.objects.filter(Content3=recoSymbolL.Content3, BaseDate__lt=queryday).order_by('-BaseDate')[0:5]
    elif recoSymbolL.RecoTypeCd == '02':
        reco_candlelist = RecoCandleL.objects.filter(Content4=recoSymbolL.Content3, BaseDate__lt=queryday).order_by('-BaseDate')[0:5]



    dict_recolist = []
    set_reco = {}

    for reco_candle in reco_candlelist:
        sim_y_data = []

        reco_queryday = reco_candle.BaseDate - datetime.timedelta(days=20)
        period_reco_candlelist = RecoCandleL.objects.filter(Symbol=reco_candle.Symbol, BaseDate__gte=reco_queryday, BaseDate__lte=reco_candle.BaseDate).order_by('BaseDate')
        if period_reco_candlelist.count() < 10:
            continue

        period_reco_candlelist = period_reco_candlelist[period_reco_candlelist.count() - 10:period_reco_candlelist.count()]
        for period_reco_candle in period_reco_candlelist:
            sim_y_data.append((period_reco_candle.Close /reco_candle.Close) * now_candle.Close)

        period_reco_candlelist2 = RecoCandleL.objects.filter(Symbol=reco_candle.Symbol, BaseDate__gt=reco_candle.BaseDate).order_by('BaseDate')[0:9]

        for period_reco_candle2 in period_reco_candlelist2:
            sim_y_data.append((period_reco_candle2.Close / reco_candle.Close) * now_candle.Close)

        sim_symbolM = get_object_or_404(SymbolM, SysMarketCd=sysmarketcd, Symbol=reco_candle.Symbol)

        graph.append(Scatter(x=x_data, y=sim_y_data,
                             mode='lines', name=sim_symbolM.Name,
                             opacity=0.6, marker_color=list_marker_color[list_marker_color_index]))

        list_marker_color_index = list_marker_color_index + 1

        set_reco = reco_candle.__dict__
        set_reco['Name'] = sim_symbolM.Name
        dict_recolist.append(set_reco)

    plot_div = plot(graph,output_type='div')

    context = {
        'plot_div': plot_div,
        'analdate': recoSymbolL.AnalDate,
        'symbol': symbolM,
        'recoSymbol': recoSymbolL,
        'reco_candlelist': dict_recolist,

    }

    return render(request, template_name, context)


def chart_disp_view(request,sysmarketcd,symbol):

    template_name = 'survDjango/chart_disp.html'

    analDateM = get_object_or_404(AnalDateM)

    symbolM = get_object_or_404(SymbolM, SysMarketCd=sysmarketcd, Symbol=symbol)

    queryday = analDateM.AnalDate - datetime.timedelta(days=20)

    logger.info(analDateM.AnalDate)

    now_candle = CandleL.objects.filter(Symbol=symbolM.Symbol, BaseDate__lte=analDateM.AnalDate).order_by('-BaseDate')[0]

    dict_simconlist = []
    simCon1List = SimContentL.objects.filter(Q(Content=now_candle.Content3) or Q(Content=now_candle.Content4)).order_by('-AnalDate')[0:5]
    logger.debug(simCon1List)
    for simCon in  simCon1List:
        dict_simconlist.append(simCon.__dict__)

    logger.debug(dict_simconlist)

    context = {
        'analdate': now_candle.BaseDate,
        'symbol': symbolM,
        'simconlist':dict_simconlist,

    }

    return render(request, template_name, context)



def chart_reco_view(request,sysmarketcd,symbol):
    template_name = 'survDjango/chart_reco.html'

    symbolM = get_object_or_404(SymbolM, SysMarketCd=sysmarketcd,Symbol=symbol)

    # from django.utils import timezone
    #
    # current_tz = timezone.get_current_timezone()
    # dt_analdate = current_tz.localize(pd.to_datetime(analDateM.AnalDate))
    #
    # logger.debug((dt_analdate)
    recoSymbolL = RecoSymbolL.objects.filter(Symbol=symbol).order_by('-AnalDate')[0]
    logger.debug(recoSymbolL)
    queryday=recoSymbolL.AnalDate - datetime.timedelta(days=20)

    candlelist = CandleL.objects.filter(Symbol=symbolM.Symbol, BaseDate__gte=queryday ,BaseDate__lte=recoSymbolL.AnalDate).order_by('BaseDate')

    candlelist = candlelist[candlelist.count()-10:candlelist.count()]

    now_candle = candlelist[candlelist.count()-1]

    x_data = [x for x in range(0, 19)]

    graph= []
    y_data = []
    list_marker_color = ['gray', 'blue', 'green', 'purple', 'pink', 'navy']
    list_marker_color_index = 0
    for candle in candlelist:
        y_data.append(candle.Close)

    graph.append(Scatter(x=x_data, y=y_data,
            mode='lines', name=symbolM.Name,
            opacity=0.8, marker_color='red'))

    if recoSymbolL.RecoTypeCd == '01':
        reco_candlelist = RecoCandleL.objects.filter(Content3=recoSymbolL.Content3, BaseDate__lt=queryday).order_by('-BaseDate')[0:5]
    elif recoSymbolL.RecoTypeCd == '02':
        reco_candlelist = RecoCandleL.objects.filter(Content4=recoSymbolL.Content3, BaseDate__lt=queryday).order_by('-BaseDate')[0:5]



    dict_recolist = []
    set_reco = {}

    for reco_candle in reco_candlelist:
        sim_y_data = []

        reco_queryday = reco_candle.BaseDate - datetime.timedelta(days=20)
        period_reco_candlelist = RecoCandleL.objects.filter(Symbol=reco_candle.Symbol, BaseDate__gte=reco_queryday, BaseDate__lte=reco_candle.BaseDate).order_by('BaseDate')
        if period_reco_candlelist.count() < 10:
            continue

        period_reco_candlelist = period_reco_candlelist[period_reco_candlelist.count() - 10:period_reco_candlelist.count()]
        for period_reco_candle in period_reco_candlelist:
            sim_y_data.append((period_reco_candle.Close /reco_candle.Close) * now_candle.Close)

        period_reco_candlelist2 = RecoCandleL.objects.filter(Symbol=reco_candle.Symbol, BaseDate__gt=reco_candle.BaseDate).order_by('BaseDate')[0:9]

        for period_reco_candle2 in period_reco_candlelist2:
            sim_y_data.append((period_reco_candle2.Close / reco_candle.Close) * now_candle.Close)

        sim_symbolM = get_object_or_404(SymbolM, SysMarketCd=sysmarketcd, Symbol=reco_candle.Symbol)

        graph.append(Scatter(x=x_data, y=sim_y_data,
                             mode='lines', name=sim_symbolM.Name,
                             opacity=0.6, marker_color=list_marker_color[list_marker_color_index]))

        list_marker_color_index = list_marker_color_index + 1

        set_reco = reco_candle.__dict__
        set_reco['Name'] = sim_symbolM.Name
        dict_recolist.append(set_reco)

    plot_div = plot(graph,output_type='div')

    context = {
        'plot_div': plot_div,
        'analdate': recoSymbolL.AnalDate,
        'symbol': symbolM,
        'recoSymbol': recoSymbolL,
        'reco_candlelist': dict_recolist,

    }

    return render(request, template_name, context)
