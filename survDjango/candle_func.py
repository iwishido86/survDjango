from random import random, randint

from astropy.io.votable.converters import Int
from django.db.models import Q, Max, Count, Sum, Avg
from django.db.models.functions import Substr
from django.forms import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from plotly.offline import plot
from plotly.graph_objs import Scatter


from .forms import UserLoginForm, SurvForm
from .models import SurvM, QuestionM, AnsM, ResultHstoryL, ResultM, ResultCommentL, SymbolM, CandleL, SimCandleL


# bulk용
def func_chk_3_1(before_candle, record):
    float_chk_1 = (record[4] - record[1]) / before_candle.Close
    chk_1 = func_make_chk_3_1(float_chk_1)

    return chk_1


def func_chk_3_2(before_candle, record):

    if record[4] == 0:
        return '-'

    if record[4] > record[1]:
        float_up = record[4]
        float_down = record[1]
    else:
        float_up = record[1]
        float_down = record[4]

    float_chk_2_1 = (record[2] - float_up) / record[4]    # high - up / close
    float_chk_2_2 = (float_down - record[3]) / record[4]  # high - up / close

    chk_2 = func_make_chk_3_2(float_chk_2_1,float_chk_2_2)

    return chk_2


def func_chk_3_3(before_candle, record):

    if before_candle.Volume == 0 or before_candle.Close == 0:
        return map_chk_3[2][2]

    float_chk_3_1 = (record[1] - before_candle.Close) / before_candle.Close    # 종가대비 시작가
    float_chk_3_2 = record[5] / before_candle.Volume  # 거래량 변동율

    chk_3 = func_make_chk_3_3(float_chk_3_1, float_chk_3_2)

    return chk_3


def create_anal_candle(symbol, before_candle, record, current_tz, pd):

    str_candle_content3 = ""

    if before_candle:

        chk_3_1 = func_chk_3_1(before_candle,record)
        chk_3_2 = func_chk_3_2(before_candle, record)
        chk_3_3 = func_chk_3_3(before_candle, record)

        str_candle_content3 = chk_3_1 + chk_3_2 + chk_3_3

        if len(before_candle.Content3) < 18:
            str_content3 = before_candle.Content3 + str_candle_content3
        else:
            str_content3 = before_candle.Content3[3:len(before_candle.Content3)] + str_candle_content3
    else:
        str_content3 = ""

    if len(str_content3) < 12:
        str_content4 = str_content3
    else:
        str_content4 = str_content3[len(str_content3)-12:]

    candle = CandleL(
        BaseDate=current_tz.localize(pd.to_datetime(record[0].tolist())),
        Symbol=symbol,
        Open=record[1],
        High=record[2],
        Low=record[3],
        Close=record[4],
        Volume=record[5],
        Change=record[6],
        Content3=str_content3,
        Content4=str_content4,
    )

    return candle


# 메이크 캔들
def func_make_chk_3_1(float_chk_1):

    # float_chk_1 몸통 + 방향
    if float_chk_1 < -0.12:
        chk_1 = "0"
    elif float_chk_1 < -0.025:
        chk_1 = "1"
    elif float_chk_1 < 0.025:
        chk_1 = "2"
    elif float_chk_1 < 0.12:
        chk_1 = "3"
    elif float_chk_1 < 0.12:
        chk_1 = "4"
    elif float_chk_1 < 0.12:
        chk_1 = "5"
    elif float_chk_1 == 1:          ## 거래금지종목일 경우 1로 옴
        chk_1 = "2"
    else:
        chk_1 = "9"

    return chk_1


map_chk_2 = [["0", "5", "A", "F", "K"],
             ["1", "6", "B", "G", "L"],
             ["2", "7", "C", "H", "M"],
             ["3", "8", "D", "I", "N"],
             ["4", "9", "E", "J", "O"],]


def func_make_chk_3_2(float_chk_2_1,float_chk_2_2):

    # float_chk_2_1 위꼬리
    # float_chk_2_2 아래꼬리

    if float_chk_2_1 < 0.03:
        chk_2_1 = 0
    elif float_chk_2_1 < 0.6:
        chk_2_1 = 1
    elif float_chk_2_1 < 0.30:      # 사실상 제거 4등급으로 나눔
        chk_2_1 = 2
    elif float_chk_2_1 < 0.30:
        chk_2_1 = 3
    else:
        chk_2_1 = 4

    if float_chk_2_2 < 0.03:
        chk_2_2 = 0
    elif float_chk_2_2 < 0.6:
        chk_2_2 = 1
    elif float_chk_2_2 < 0.30:      # 사실상 제거 4등급으로 나눔
        chk_2_2 = 2
    elif float_chk_2_2 < 0.30:
        chk_2_2 = 3
    else:
        chk_2_2 = 4

    return map_chk_2[chk_2_1][chk_2_2]


map_chk_3 = [["0", "5", "A", "F", "K", "P"],
             ["1", "6", "B", "G", "L", "Q"],
             ["2", "7", "C", "H", "M", "R"],
             ["3", "8", "D", "I", "N", "S"],
             ["4", "9", "E", "J", "O", "T"],]


def func_make_chk_3_3(float_chk_3_1, float_chk_3_2):

    # float_chk_3_1  종가대비 시작가
    # float_chk_3_2  거래량 변동

    if float_chk_3_1 < -0.05:
        chk_3_1 = 0
    elif float_chk_3_1 < -0.020:
        chk_3_1 = 1
    elif float_chk_3_1 < 0.020:
        chk_3_1 = 2
    elif float_chk_3_1 < 0.05:
        chk_3_1 = 3
    else:
        chk_3_1 = 4

    if float_chk_3_2 < 1/3:
        chk_3_2 = 0
    elif float_chk_3_2 < 2:
        chk_3_2 = 1
    elif float_chk_3_2 < 9:
        chk_3_2 = 2
    elif float_chk_3_2 < 9:
        chk_3_2 = 3
    elif float_chk_3_2 < 9:
        chk_3_2 = 4
    else:
        chk_3_2 = 5

    return map_chk_3[chk_3_1][chk_3_2]


#update용
def func_chk_3_1_up(before_candle, candle):
    float_chk_1 = (candle.Close - candle.Open) / before_candle.Close
    chk_1 = func_make_chk_3_1(float_chk_1)

    return chk_1


def func_chk_3_2_up(before_candle, candle):

    if  candle.Close == 0:
        return '-'

    if candle.Close > candle.Open:
        float_up = candle.Close
        float_down = candle.Open
    else:
        float_up = candle.Open
        float_down = candle.Close

    float_chk_2_1 = (candle.High - float_up) / candle.Close    # high - up / close
    float_chk_2_2 = (float_down - candle.Low) / candle.Close  # high - up / close

    chk_2 = func_make_chk_3_2(float_chk_2_1, float_chk_2_2)

    return chk_2


def func_chk_3_3_up(before_candle, candle):

    if before_candle.Volume == 0 or before_candle.Close == 0:
        return '-'

    float_chk_3_1 = (candle.Open - before_candle.Close) / before_candle.Close    # 종가대비 시작가
    float_chk_3_2 = candle.Volume / before_candle.Volume  # 거래량 변동율

    chk_3 = func_make_chk_3_3(float_chk_3_1, float_chk_3_2)

    return chk_3


def update_anal_candle(symbol, before_candle, candle):

    str_candle_content3 = ""

    if before_candle:

        chk_3_1 = func_chk_3_1_up(before_candle, candle)
        chk_3_2 = func_chk_3_2_up(before_candle, candle)
        chk_3_3 = func_chk_3_3_up(before_candle, candle)

        str_candle_content3 = chk_3_1 + chk_3_2 + chk_3_3

        if len(before_candle.Content3) < 18:
            str_content3 = before_candle.Content3 + str_candle_content3
        else:
            str_content3 = before_candle.Content3[3:len(before_candle.Content3)] + str_candle_content3
    else:
        str_content3 = ""

    if len(str_content3) < 12:
        candle.str_content4 = str_content3
    else:
        candle.str_content4 = str_content3[len(str_content3)-12:]

    candle.Content3 = str_content3

    return candle
