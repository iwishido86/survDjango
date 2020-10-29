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

#http://127.0.0.1:8000/symbol/
def sym_index_view(request):
    template_name = 'survDjango/ca_init.html'

    analDateM = AnalDateM.objects.filter()[0]
    #sim_candlelist = SimCandleL.objects.filter(BaseDate=analDateM.AnalDate).values('Symbol').annotate(SimCandleCnt=Count('Content1')).annotate(AvgContent1=Avg('Content1')).filter(BaseDate=analDateM.AnalDate, AvgContent1__gte=7).order_by('-SimCandleCnt','-AvgContent1')[0:10]
    #sim_candlelist = SimCandleL.objects.filter(BaseDate=analDateM.AnalDate, AvgContent1__gte=10).values(Symbol').annotate(SimCandleCnt=Count('Content1'), AvgContent1=Avg('Content1')).order_by('-AvgContent1')[0:10]
    #Product.objects.values('date_created')       .annotate(available=Count('available_quantity'))

    dict_simCon1List = []
    set_simCon = {}
    simCon1List = SimContentL.objects.filter(AnalDate=analDateM.AnalDate, SimTypeCd='02').order_by('-Content1')[0:10]

    for simCon1 in simCon1List:

        candleCon1 = CandleL.objects.filter(BaseDate=analDateM.AnalDate,Content4=simCon1.Content).order_by('Symbol', 'BaseDate')[0]

        set_simCon = simCon1.__dict__
        sim_symbolM = get_object_or_404(SymbolM, SysMarketCd='KRX', Symbol=candleCon1.Symbol)
        set_simCon['NAME'] = sim_symbolM.Name
        dict_simCon1List.append(set_simCon)

    logger.info(dict_simCon1List)

    dict_simCon2List = []
    set_simCon = {}
    simCon1List = SimContentL.objects.filter(AnalDate=analDateM.AnalDate, SimTypeCd='01').order_by('-Content1')[0:10]

    for simCon1 in simCon1List:
        candleCon1 = \
        CandleL.objects.filter(BaseDate=analDateM.AnalDate, Content3=simCon1.Content).order_by('Symbol', 'BaseDate')[0]

        set_simCon = simCon1.__dict__
        sim_symbolM = get_object_or_404(SymbolM, SysMarketCd='KRX', Symbol=candleCon1.Symbol)
        set_simCon['NAME'] = sim_symbolM.Name
        dict_simCon2List.append(set_simCon)

    logger.info(dict_simCon2List)

    context = {
        dict_simCon1List : 'simcon1list',
        dict_simCon2List: 'simcon1list',
    }

    return render(request, template_name, context)

#https://kimsudal.com/anal_init/KRX
def ca_init_view(request,sysmarketcd):
    template_name = 'survDjango/ca_init.html'

    #%matplotlib   inline
    import matplotlib.pyplot as plt
    import FinanceDataReader as fdr
    import pandas as pd
    # plt.rcParams["font.family"] = 'nanummyeongjo'
    # plt.rcParams["figure.figsize"] = (14, 4)
    # plt.rcParams['lines.linewidth'] = 2
    # plt.rcParams["axes.grid"] = True
    #
    # logger.info(fdr.__version__)

    # 한국거래소 상장종목 전체
    df_krx = fdr.StockListing(sysmarketcd)
    # 2581: {'Symbol': '238490', 'Market': 'KOSDAQ', 'Name': '힘스', 'Sector':
    # '특수 목적용 기계 제조업', 'Industry': 'OLED Mask 인장기, OLED Mask 검사기 등', 'ListingDate': Timestamp('2017-07-20
    #  00:00:00'), 'SettleMonth': '12월', 'Representative': '김주환', 'HomePage': 'http://www.hims.co.kr', 'Region': '인천
    # 광역시'
    #logger.info(df_krx.T.to_dict())

    dict_krx = df_krx.T.to_dict()

    # symbolMall = SymbolM.objects.all()
    # symbolMall.delete()

    for sequrity in dict_krx:
        logger.info(dict_krx[sequrity])

        symbolM, created = SymbolM.objects.get_or_create(
            SysMarketCd=sysmarketcd,
            Symbol=dict_krx[sequrity]['Symbol'],
        )

        symbolM.Symbol = dict_krx[sequrity]['Symbol']
        symbolM.Market = dict_krx[sequrity]['Market']
        symbolM.Name = dict_krx[sequrity]['Name']
        symbolM.Sector = dict_krx[sequrity]['Sector']

        dict_krx[sequrity]['ListingDate'] = pd.to_datetime(dict_krx[sequrity]['ListingDate'])

        #symbolM.ListingDate = dict_krx[sequrity]['ListingDate']
        symbolM.SettleMonth = dict_krx[sequrity]['SettleMonth']
        symbolM.Representative = dict_krx[sequrity]['Representative']
        symbolM.HomePage = dict_krx[sequrity]['HomePage']
        symbolM.Region = dict_krx[sequrity]['Region']

        symbolM.save()

    # resultHstoryL = ResultHstoryL.objects.all()
    # resultHstoryL.delete()

    context = {

    }

    return render(request, template_name, context)


def sym_bulk_view(request,sysmarketcd,symbol):
    template_name = 'survDjango/ca_init.html'

    from django.utils import timezone

    current_tz = timezone.get_current_timezone()

    refreshDate = datetime.datetime.now()

    # 초기화
    model_instances = []

    symbolMlist = SymbolM.objects.filter(Symbol__gte=symbol).order_by('Symbol')[0:50]

    for symbolM in symbolMlist :

        before_candle = CandleL().__init__()
        logger.info(symbolM.Symbol)

        CandleL.objects.filter(Symbol=symbolM.Symbol).delete()

        df_sym = fdr.DataReader(symbolM.Symbol,'2010-01-01')
        dict_sym = df_sym.to_records()

        for record in dict_sym:

            candle = create_anal_candle(symbolM.Symbol, before_candle, record, current_tz, pd)
            model_instances.append(candle)
            before_candle = candle
        #logger.info(model_instances)

    CandleL.objects.bulk_create(model_instances)

    return HttpResponseRedirect('/symbol/bulk/' + symbolMlist[49].SysMarketCd + '/' + symbolMlist[49].Symbol )
#    return render(request, template_name, {})


#http://127.0.0.1:8000/symbol/day_update/KRX/2020-10-20
def sym_day_update_view(request,sysmarketcd,basedate):
    template_name = 'survDjango/ca_init.html'

    current_tz = timezone.get_current_timezone()

    dt_basedate = current_tz.localize(pd.to_datetime(basedate))
    queryday = dt_basedate + datetime.timedelta(days=1)

    logger.info(queryday.strftime("%Y-%m-%d"))
    candlelist = CandleL.objects.filter(BaseDate=basedate).order_by('Symbol','BaseDate')

    model_instances = []

    for candlel in candlelist :

        #초기화
        before_candle = candlel
        logger.info(candlel.Symbol)

        df_sym = fdr.DataReader(candlel.Symbol, queryday.strftime("%Y-%m-%d"))
        dict_sym = df_sym.to_records()

        for record in dict_sym:

            candle = create_anal_candle(candlel.Symbol, before_candle, record, current_tz, pd)
            model_instances.append(candle)
            before_candle = candle
        #logger.info(model_instances)

    CandleL.objects.bulk_create(model_instances)

#    return HttpResponseRedirect('/symbol/bulk/' + symbolMlist[499].SysMarketCd + '/' + symbolMlist[499].Symbol )
    return render(request, template_name, {})


def sym_anal_view(request,sysmarketcd,symbol,analdate):
    template_name = 'survDjango/sym_anal.html'

    current_tz = timezone.get_current_timezone()
    dt_analdate = current_tz.localize(pd.to_datetime(analdate))
    #최근영업일
    AnalDateM.objects.filter().delete()
    AnalDateM(AnalDate=dt_analdate).save()

    today =  current_tz.localize(datetime.datetime.now())
    queryday = today - datetime.timedelta(days=10)

    logger.info(dt_analdate)
    candlelist = CandleL.objects.filter(Symbol__gte=symbol, BaseDate=analdate).order_by('Symbol')[0:50]

    dict_candlelist = []
    model_instances = []

    for candle in candlelist :
        #TODO 튜닝포인트

        logger.info("1::"+candle.Symbol + "::" + candle.Content3 + "::" + len(candle.Content3.split('207')).__str__())

        if candle.Content3 == '20C20C20C20C20C20C20C20C':
            continue
        if len(candle.Content3.split('207')) > 6:
            continue

        set_candle = candle.__dict__
        set_candle['mappingCon3'] = candle.Content3

        dict_sim_candle = []
        set_sim_candle = {}

        sim_query_day = candle.BaseDate - datetime.timedelta(days=30)

        del_sim_candlelist= SimCandleL.objects.filter(Symbol=candle.Symbol, BaseDate=candle.BaseDate)
        del_sim_candlelist.delete()
        logger.info("2::" + candle.Symbol)
        sim_candlelist = CandleL.objects.filter( Content3=candle.Content3, BaseDate__lt=sim_query_day).order_by('-BaseDate')[0:5]

        if sim_candlelist.count() == 0:
            set_candle['mappingCon3'] = set_candle['mappingCon3'][9:]
            sim_candlelist = CandleL.objects.filter(~Q(Symbol=candle.Symbol),Content4=candle.Content4,BaseDate__lt=sim_query_day).order_by('-BaseDate')[0:5]

        logger.info("3::" + candle.Symbol)
        #sim_candlelist = CandleL.objects.filter(~Q(Symbol=symbolM.Symbol),Content3=set_candle['mappingCon3'],BaseDate__lt=sim_query_day).order_by('-BaseDate')[0:10]
        for sim_candle in sim_candlelist:

            #candle = CandleL.objects.filter(Symbol=symbolM.Symbol, BaseDate__gt=queryday).order_by('-BaseDate')[0:1]

            startday = sim_candle.BaseDate + datetime.timedelta(days=1)
            endday = sim_candle.BaseDate + datetime.timedelta(days=10)

            avg_close = CandleL.objects.filter(Symbol=sim_candle.Symbol, BaseDate__gt=startday , BaseDate__lt=endday ).aggregate(AvgClose=Avg('Close'))
            if avg_close['AvgClose']:
                content1 = (avg_close['AvgClose'] - sim_candle.Close ) * 100 / sim_candle.Close
            else:
                content1 = 0

            set_sim_candle = sim_candle.__dict__
            dict_sim_candle.append(set_sim_candle)

            simcandle = SimCandleL(
                BaseDate=candle.BaseDate,
                Symbol=candle.Symbol,
                SimBaseDate=sim_candle.BaseDate,
                SimSymbol=sim_candle.Symbol,
                SimTypeCd='01',
                ChartNum=candle.Close/sim_candle.Close,
                Content1=content1,
                Content2=0,
            )
            model_instances.append(simcandle)

        set_candle['simCandlelist'] = dict_sim_candle

        dict_candlelist.append(set_candle)

    SimCandleL.objects.bulk_create(model_instances)


    #logger.info(dict_candlelist)
    context = {
        'candlelist' : dict_candlelist
    }
    return HttpResponseRedirect('/symbol/anal/' + sysmarketcd + '/' + candlelist[49].Symbol  + '/' + analdate )
    #return render(request, template_name, context)


#http://127.0.0.1:8000/symbol/anal2/KRX/2020-10-22
def sym_anal2_view(request,sysmarketcd,analdate):
    template_name = 'survDjango/sym_anal.html'
    logger.debug('3333')
    from django.utils import timezone

    current_tz = timezone.get_current_timezone()
    dt_analdate = current_tz.localize(pd.to_datetime(analdate))
    #최근영업일
    AnalDateM.objects.filter().delete()
    AnalDateM(AnalDate=analdate).save()

    today =  current_tz.localize(datetime.datetime.now())
    queryday = today - datetime.timedelta(days=10)

    #sim_candlelist = SimCandleL.objects.filter(BaseDate=analDateM.AnalDate).values('Symbol').annotate(SimCandleCnt=Count('Content1')).annotate(AvgContent1=Avg('Content1')).filter(BaseDate=analDateM.AnalDate, AvgContent1__gte=7).order_by('-SimCandleCnt','-AvgContent1')[0:10]
    #sim_candlelist = SimCandleL.objects.filter(BaseDate=analDateM.AnalDate, AvgContent1__gte=10).values(Symbol').annotate(SimCandleCnt=Count('Content1'), AvgContent1=Avg('Content1')).order_by('-AvgContent1')[0:10]
    #Product.objects.values('date_created')       .annotate(available=Count('available_quantity'))
    #logger.info(sim_candlelist)

    del_simContentList = SimContentL.objects.filter(AnalDate=analdate)
    del_simContentList.delete()
    #logger.info(dt_analdate)
    #candlelist = CandleL.objects.filter(Symbol__gte=symbol, BaseDate=analdate).order_by('Symbol')[0:50]
    #candleGrplist = CandleL.objects.filter(BaseDate=analdate).values('Content3').annotate(CandleCnt=Count('Content3')).order_by('-CandleCnt')
    candleGrplist = CandleL.objects.filter().values('Content3').annotate(CandleCnt=Count('Content3')).annotate(
        MaxBaseDate=Max('BaseDate')).filter(MaxBaseDate=analdate).order_by('-CandleCnt')

    logger.info(candleGrplist.count().__str__())

    dict_candlelist = []
    model_instances = []
    index = 0
    for candleGrp in candleGrplist :
        #TODO 튜닝포인트

        logger.info("1::"+ candleGrp["Content3"] + "::" + candleGrp["CandleCnt"].__str__() + "::" + index.__str__())
        index = index + 1
        # AnalDate = models.DateTimeField()
        # SimTypeCd = models.CharField(max_length=2, help_text="유사유형:01:Content3:02:Content4:03:안함:04:없음")
        # Content = models.CharField(max_length=100, blank=True, null=True)
        # SimSymbolCnt = models.FloatField(default=0, help_text="갯수")
        # Content1 = models.FloatField(default=0, help_text="단기수익률")
        # Content2 = models.FloatField(default=0, help_text="장기수익률")
        # Content3 = models.CharField(max_length=100, blank=True, null=True)
        # Content4 = models.CharField(max_length=100, blank=True, null=True)
        # 20개 이상
        if candleGrp["CandleCnt"] > 10 \
            or len(candleGrp["Content3"]) < 24:
            simcandle = SimContentL(
                AnalDate=analdate,
                SimTypeCd='03',
                Content=candleGrp["Content3"],
                SimSymbolCnt=candleGrp["CandleCnt"],
                Content1=0,
                Content2=0,
                Content3='',
                Content4='',
            )
            model_instances.append(simcandle)
            continue

        #하나만 있는 경우
        elif candleGrp["CandleCnt"] <= 1:
            simcandle = SimContentL(
                AnalDate=analdate,
                SimTypeCd='04',
                Content=candleGrp["Content3"],
                SimSymbolCnt=0,
                Content1=0,
                Content2=0,
                Content3='',
                Content4='',
            )
            model_instances.append(simcandle)
            continue

        dict_sim_candle = []
        set_sim_candle = {}

        sim_query_day = dt_analdate - datetime.timedelta(days=30)

        sim_candlelist = CandleL.objects.filter( Content3=candleGrp["Content3"], BaseDate__lt=sim_query_day).order_by('-BaseDate')[0:5]

        logger.info("3::" + sim_candlelist.count().__str__())

        sum_content1 = 0
        #sim_candlelist = CandleL.objects.filter(~Q(Symbol=symbolM.Symbol),Content3=set_candle['mappingCon3'],BaseDate__lt=sim_query_day).order_by('-BaseDate')[0:10]
        for sim_candle in sim_candlelist:

            #candle = CandleL.objects.filter(Symbol=symbolM.Symbol, BaseDate__gt=queryday).order_by('-BaseDate')[0:1]

            startday = sim_candle.BaseDate + datetime.timedelta(days=1)
            endday = sim_candle.BaseDate + datetime.timedelta(days=10)

            avg_close = CandleL.objects.filter(Symbol=sim_candle.Symbol, BaseDate__gte=startday , BaseDate__lte=endday ).aggregate(AvgClose=Avg('Close'))
            if avg_close['AvgClose']:
                sum_content1 = sum_content1 + (avg_close['AvgClose'] - sim_candle.Close ) * 100 / sim_candle.Close

        if sim_candlelist.count() == 0:
            simcandle = SimContentL(
                AnalDate=analdate,
                SimTypeCd='04',
                Content=candleGrp["Content3"],
                SimSymbolCnt=0,
                Content1=0,
                Content2=0,
                Content3='',
                Content4='',
            )
            model_instances.append(simcandle)
        else:

            simcandle = SimContentL(
                AnalDate=analdate,
                SimTypeCd='01',
                Content=candleGrp["Content3"],
                SimSymbolCnt=candleGrp["CandleCnt"],
                Content1=sum_content1/sim_candlelist.count(),
                Content2=0,
                Content3='',
                Content4='',
            )
            model_instances.append(simcandle)


    SimContentL.objects.bulk_create(model_instances)


    #logger.info(dict_candlelist)
    context = {
    }
    return HttpResponseRedirect('/symbol/anal3/' + sysmarketcd + '/' + analdate)

    #return render(request, template_name, context)


#http://127.0.0.1:8000/symbol/anal3/KRX/2020-10-20
def sym_anal3_view(request,sysmarketcd,analdate):
    template_name = 'survDjango/sym_anal.html'

    from django.utils import timezone

    current_tz = timezone.get_current_timezone()
    dt_analdate = current_tz.localize(pd.to_datetime(analdate))
    #최근영업일
    AnalDateM.objects.filter().delete()
    AnalDateM(AnalDate=analdate).save()

    today =  current_tz.localize(datetime.datetime.now())
    queryday = today - datetime.timedelta(days=10)

    #candleGrplist = CandleL.objects.filter(BaseDate=analdate).values('Content4').annotate(CandleCnt=Count('Content4')).order_by('-CandleCnt')
    candleGrplist = CandleL.objects.filter().values('Content4').annotate(CandleCnt=Count('Content4')).annotate(
        MaxBaseDate=Max('BaseDate')).filter(MaxBaseDate=analdate).order_by('-CandleCnt')
    logger.info(candleGrplist.count().__str__())


    dict_candlelist = []
    model_instances = []
    index = 0
    for candleGrp in candleGrplist :
        #TODO 튜닝포인트

        logger.info("1::"+ candleGrp["Content4"] + "::" + candleGrp["CandleCnt"].__str__() + "::" + index.__str__())
        index = index + 1

        if candleGrp["CandleCnt"] > 10 \
                or len(candleGrp["Content4"]) < 12:

            continue
        elif candleGrp["CandleCnt"] <= 1 :
            continue
        dict_sim_candle = []
        set_sim_candle = {}

        sim_query_day = dt_analdate - datetime.timedelta(days=30)

        sim_candlelist = CandleL.objects.filter( Content4=candleGrp["Content4"], BaseDate__lt=sim_query_day).order_by('-BaseDate')[0:5]

        logger.info("3::" + sim_candlelist.count().__str__())

        sum_content1 = 0
        #sim_candlelist = CandleL.objects.filter(~Q(Symbol=symbolM.Symbol),Content3=set_candle['mappingCon3'],BaseDate__lt=sim_query_day).order_by('-BaseDate')[0:10]
        for sim_candle in sim_candlelist:

            #candle = CandleL.objects.filter(Symbol=symbolM.Symbol, BaseDate__gt=queryday).order_by('-BaseDate')[0:1]

            startday = sim_candle.BaseDate + datetime.timedelta(days=1)
            endday = sim_candle.BaseDate + datetime.timedelta(days=10)

            avg_close = CandleL.objects.filter(Symbol=sim_candle.Symbol, BaseDate__gte=startday , BaseDate__lte=endday ).aggregate(AvgClose=Avg('Close'))
            if avg_close['AvgClose']:
                sum_content1 = sum_content1 + (avg_close['AvgClose'] - sim_candle.Close ) * 100 / sim_candle.Close

        if sim_candlelist.count() == 0:
            continue
        else:

            simcandle = SimContentL(
                AnalDate=analdate,
                SimTypeCd='02',
                Content=candleGrp["Content4"],
                SimSymbolCnt=sim_candlelist.count(),
                Content1=sum_content1/sim_candlelist.count(),
                Content2=0,
                Content3='',
                Content4='',
            )
            model_instances.append(simcandle)


    SimContentL.objects.bulk_create(model_instances)


    #logger.info(dict_candlelist)
    context = {
    }
    return HttpResponseRedirect('/symbol/anal4/' + sysmarketcd + '/' + analdate)


#http://127.0.0.1:8000/symbol/anal4/KRX/2020-10-22
#추천종목 인서트
def sym_anal4_view(request,sysmarketcd,analdate):
    template_name = 'survDjango/ca_init.html'

    AnalDateM.objects.filter().delete()
    AnalDateM(AnalDate=analdate).save()

    #analDateM = AnalDateM.objects.filter()[0]

    RecoSymbolL.objects.filter(AnalDate=analdate).delete()

    # 8개 캔들 찾기 -> RecoSymbolL 저장 , RecoCandleL저장
    # 3개 이상 수익률 우선
    simCon1List = SimContentL.objects.filter(AnalDate=analdate, SimTypeCd='01').order_by('-Content1')[0:20]

    for simCon1 in simCon1List:

        sim_queryday = simCon1.AnalDate - datetime.timedelta(days=20)
        # 그 candle 찾음
        candleCon1 = CandleL.objects.filter(BaseDate=analdate,Content3=simCon1.Content).order_by('Symbol', 'BaseDate')[0]

        #sim_symbolM = get_object_or_404(SymbolM, SysMarketCd='KRX', Symbol=candleCon1.Symbol)
        RecoSymbolL(
            AnalDate=analdate,
            Symbol=candleCon1.Symbol,
            RecoTypeCd='01',##8개비교
            SimSymbolCnt=simCon1.SimSymbolCnt,
            Content1=simCon1.Content1,
            Content2=simCon1.Content2,
            Content3=simCon1.Content,
            Close=candleCon1.Close,
            NowClose=candleCon1.Close,
        ).save()

        #그 이전에 같은 패턴 캔들 찾음
        sim_candlelist = CandleL.objects.filter(Content3=simCon1.Content, BaseDate__lte=sim_queryday).order_by('-BaseDate')[0:5]
        for sim_candle in sim_candlelist:

            start_date = sim_candle.BaseDate - datetime.timedelta(days=30)
            end_date = sim_candle.BaseDate + datetime.timedelta(days=35)

            periode_sim_candlelist = CandleL.objects.filter(Symbol=sim_candle.Symbol, BaseDate__gte=start_date, BaseDate__lte=end_date).order_by('BaseDate')
            logger.info(candleCon1.Symbol+":::" + sim_candle.Symbol + ":::" + periode_sim_candlelist.count().__str__())
            for periode_sim_candle in periode_sim_candlelist:
                RecoCandleL(
                    CandleId=periode_sim_candle.CandleId,
                    BaseDate=periode_sim_candle.BaseDate,
                    Symbol=periode_sim_candle.Symbol,
                    Open=periode_sim_candle.Open,
                    High=periode_sim_candle.High,
                    Low=periode_sim_candle.Low,
                    Close=periode_sim_candle.Close,
                    Volume=periode_sim_candle.Volume,
                    Change=periode_sim_candle.Change,
                    Content1=periode_sim_candle.Content1,
                    Content2=periode_sim_candle.Content2,
                    Content3=periode_sim_candle.Content3,
                    Content4=periode_sim_candle.Content4,
                    Content5=periode_sim_candle.Content5,
                    Content6=periode_sim_candle.Content6,
                ).save()

    # 4개 캔들 찾기 -> RecoSymbolL 저장 , RecoCandleL저장
    # 3개 이상 수익률 우선
    simCon1List = SimContentL.objects.filter(AnalDate=analdate, SimTypeCd='02').order_by('-Content1')[0:20]

    for simCon1 in simCon1List:

        sim_queryday = simCon1.AnalDate - datetime.timedelta(days=20)
        # 그 candle 찾음
        candleCon1 = \
        CandleL.objects.filter(BaseDate=analdate, Content4=simCon1.Content).order_by('Symbol', 'BaseDate')[0]

        # sim_symbolM = get_object_or_404(SymbolM, SysMarketCd='KRX', Symbol=candleCon1.Symbol)
        RecoSymbolL(
            AnalDate=analdate,
            Symbol=candleCon1.Symbol,
            RecoTypeCd='02',  ##4개비교
            SimSymbolCnt=simCon1.SimSymbolCnt,
            Content1=simCon1.Content1,
            Content2=simCon1.Content2,
            Content3=simCon1.Content,
            Close=candleCon1.Close,
            NowClose=candleCon1.Close,
        ).save()

        # 그 이전에 같은 패턴 캔들 찾음
        sim_candlelist = CandleL.objects.filter(Content4=simCon1.Content, BaseDate__lte=sim_queryday).order_by('-BaseDate')[0:5]
        for sim_candle in sim_candlelist:

            start_date = sim_candle.BaseDate - datetime.timedelta(days=30)
            end_date = sim_candle.BaseDate + datetime.timedelta(days=35)

            periode_sim_candlelist = CandleL.objects.filter(Symbol=sim_candle.Symbol, BaseDate__gte=start_date, BaseDate__lte=end_date).order_by('BaseDate')
            logger.info(candleCon1.Symbol + ":::" + sim_candle.Symbol + ":::" + periode_sim_candlelist.count().__str__())
            for periode_sim_candle in periode_sim_candlelist:
                RecoCandleL(
                    CandleId=periode_sim_candle.CandleId,
                    BaseDate=periode_sim_candle.BaseDate,
                    Symbol=periode_sim_candle.Symbol,
                    Open=periode_sim_candle.Open,
                    High=periode_sim_candle.High,
                    Low=periode_sim_candle.Low,
                    Close=periode_sim_candle.Close,
                    Volume=periode_sim_candle.Volume,
                    Change=periode_sim_candle.Change,
                    Content1=periode_sim_candle.Content1,
                    Content2=periode_sim_candle.Content2,
                    Content3=periode_sim_candle.Content3,
                    Content4=periode_sim_candle.Content4,
                    Content5=periode_sim_candle.Content5,
                    Content6=periode_sim_candle.Content6,
                ).save()


    # 과거 RecoSymbolL NowClose 업데이트
    # 과거 RecoSymbolL NowClose 업데이트
    analDateM = get_object_or_404(AnalDateM)
    query_date = analDateM.AnalDate - datetime.timedelta(days=10)

    recoSymbolLlist = RecoSymbolL.objects.filter(AnalDate__gte=query_date, AnalDate__lt=analDateM.AnalDate)

    for recoSymbolL in recoSymbolLlist:

        recoSymbol_candel = CandleL.objects.filter(BaseDate=analdate, Symbol=recoSymbolL.Symbol).order_by('BaseDate')[0]
        recoSymbolL.NowClose = recoSymbol_candel.Close
        recoSymbolL.save()

    context = {
    }

    return render(request, template_name, context)



#http://127.0.0.1:8000/symbol/reco/KRX/256840
def sym_reco_view(request,sysmarketcd,symbol):
    template_name = 'survDjango/sym_disp.html'

    symbolM = get_object_or_404(SymbolM, SysMarketCd=sysmarketcd,Symbol=symbol)
    analDateM = get_object_or_404(AnalDateM)

    # from django.utils import timezone
    #
    # current_tz = timezone.get_current_timezone()
    # dt_analdate = current_tz.localize(pd.to_datetime(analDateM.AnalDate))
    #
    # logger.info(dt_analdate)
    recoSymbolL = RecoSymbolL.objects.filter(Symbol=symbol, AnalDate=analDateM.AnalDate)[0]
    logger.info(recoSymbolL)
    queryday=analDateM.AnalDate - datetime.timedelta(days=20)

    candlelist = CandleL.objects.filter(Symbol=symbolM.Symbol, BaseDate__gte=queryday ,BaseDate__lte=analDateM.AnalDate).order_by('BaseDate')

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

    logger.info(reco_candlelist)

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

    plot_div = plot(graph,output_type='div')

    context = {
        'plot_div': plot_div,
        'analdate': analDateM.AnalDate.strftime("%Y-%m-%d"),
        'symbol': symbolM,
        'recoSymbol': recoSymbolL,
        'reco_candlelist': reco_candlelist,

    }

    return render(request, template_name, context)


def sym_reupdate_view(request,sysmarketcd,symbol):
    template_name = 'survDjango/ca_init.html'

    symbolMlist = SymbolM.objects.filter(Symbol__gte=symbol).order_by('Symbol')[0:500]

    for symbolM in symbolMlist :
        logger.info(symbolM.Symbol)
        model_instances = []
        before_candle = CandleL().__init__()
        candlelist = CandleL.objects.filter(Symbol=symbolM.Symbol).order_by('BaseDate')
        for candle in candlelist:
            
            candle = update_anal_candle(symbolM.Symbol, before_candle, candle)
            before_candle = candle
            model_instances.append(candle)

        candlelist.delete()
        CandleL.objects.bulk_create(model_instances)
        #candlelist.update()
        #CandleL.objects.bulk_update(candlelist.values(), ['Content3'], batch_size=500)

    return HttpResponseRedirect('/symbol/reupdate/' + symbolMlist[499].SysMarketCd + '/' + symbolMlist[499].Symbol )
    #return render(request, template_name, {})
#
#
#
# def knight_select_view(request, username):
#     template_name = 'survDjango/knight_select.html'
#
#     if request.method == 'POST':
#         form = KnightSelectForm(request.POST)
#
#         username = request.POST.get('username')
#
#         user, created = User.objects.get_or_create(
#             username=username
#         )
#
#         user.username = username
#         user.readyYn = 'Y'
#         user.joinYn = 'Y'
#
#         user.save()
#
#         delSelectKnightList = SelectKnight.objects.filter(username=username)
#

#         delSelectKnightList.delete()
#
#         knightliststr = request.POST.get('knightliststr')
#
#         knightlist = knightliststr.split(';')
#
#         for knightId in knightlist :
#             if knightId == '':
#                 break
#
#             selectKnight, created = SelectKnight.objects.get_or_create(
#                 username=username,
#                 knightId=knightId
#             )
#             selectKnight.save()
#
#         return HttpResponseRedirect(
#             '/mycard/%s' % username
#         )
#
#     else:
#         form = KnightSelectForm()
#         form.fields['username'].initial = username
#         knightlist = Knight.objects.filter(~Q(knightId=9)).order_by('knightId')
#         context = {
#             'form': form,
#             'username':username,
#             'knightlist': knightlist,
#         }
#
#     return render(request, template_name, context)

#
# def assin_view(request):
#     template_name = 'survDjango/start.html'
#     weight = 5
#     assinnum = 0
#
#     #참여 유저수
#     joinusercnt = User.objects.filter(joinYn='Y').count()
#
#     # 게임 setting
#     gamecnt = Game.objects.filter(completeYn='N').count()
#
#     if gamecnt > 0 :
#         return render(request, 'survDjango/error.html', {'errstr': '아직 진행중인 게임이 있습니다. 게임을 취소하고 다시 시도하십시오'} )
#
#     gameIdObj = Game.objects.all().order_by('-gameId')
#
#     if gameIdObj :
#         gameId = gameIdObj[0].gameId + 1
#     else:
#         gameId= 1
#
#     game = Game.objects.create()
#
#     game.gameId = gameId
#     game.joinUserCnt = joinusercnt
#
#     game.save()
#
#
#     # 카드 세팅 초기화
#     userlist = User.objects.filter(joinYn='Y')
#
#     for user in userlist:
#         user.assinKnightId = 0
#         user.save()
#
#
#     # 카드 지정 완료 유저 Q
#     assineduserq = Q()
#     for i in range(1,joinusercnt+1):
#
#         q = Q(knightId=i)
#         q.add(~assineduserq ,q.AND)
#
#         selectknightlist = SelectKnight.objects.filter(q)
#
#         #for selectknight in selectknightlist:
#             #logger.info(selectknight.username + selectknight.knightId.__str__() )
#
#         selectknightcnt = weight * selectknightlist.count()
#
#         assinnum = randint(1,joinusercnt + selectknightcnt +1 - i)
#
#         if assinnum <= selectknightcnt:
#             assinedusername = selectknightlist[ ( (assinnum-1)/weight).__int__()].username
#
#         else:
#             unassineduserlist = User.objects.filter(Q(joinYn='Y') & Q(assinKnightId=0))
#             assinedusername = unassineduserlist[(assinnum - selectknightcnt-1)].username
#
#         user = get_object_or_404(User, username=assinedusername)
#         user.assinKnightId = i
#         user.save()
#
#         assineduserq.add( Q(username=assinedusername) , assineduserq.OR)
#
#     return HttpResponseRedirect('/start/' )


    # def delete_view(request,username):
    # template_name = 'survDjango/start.html'
    #
    # user = get_object_or_404(User, username=username)
    #
    # user.delete()
    #
    # return HttpResponseRedirect('/start/' )