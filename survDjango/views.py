from random import random, randint

from astropy.io.votable.converters import Int
from django.db.models import Q, Max, Count, Sum
from django.forms import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .forms import UserLoginForm, SurvForm
from .models import SurvM, QuestionM, AnsM, ResultHstoryL, ResultM
from .serializers import RegistrationUserSerializer


def surv_view(request,survid):
    template_name = 'survDjango/surv.html'

    if request.method == 'POST':

        survId = request.POST.get('survId', '')
        questionNum = request.POST.get('questionNum', '')
        historyContent = ""
        point = 0
        for i in range(1,int(questionNum)+1):
            #print(request.POST.get('radio'+i.__str__(), ''))
            ansId = request.POST.get('radio'+i.__str__())

            # 여기 튜닝 원쿼리로
            ans = get_object_or_404(AnsM, survId=survid, questionId=i, ansId=ansId)

            point = point + int(ans.point)

            historyContent = historyContent + ansId + "-" + ans.point.__str__() + ":"

        # 결과
        resultId = ""

        # 여기 튜닝 원쿼리로
        result = get_object_or_404(ResultM, survId=survid, pointBottom__lte=point, pointTop__gte=point)
        result.cnt = result.cnt + 1
        result.save()

        surv = get_object_or_404(SurvM, survId=survId)

        surv.cnt = surv.cnt + 1
        surv.save()

        # 내역 저장
        resultHstoryL  = ResultHstoryL.objects.create()

        resultHstoryL.survId = survId
        resultHstoryL.resultId = result.resultId
        resultHstoryL.content = historyContent + ":::" + point.__str__()
        resultHstoryL.content2 = point.__str__()

        resultHstoryL.save()

        #sumresult= ResultHstoryL.objects.values('resultId').annotate(totalcnt=Count('resultId'))
        #print(sumresult)

        #sumresult= ResultHstoryL.objects.count()
        #print(sumresult)


        return HttpResponseRedirect(
            '/result/' + survId+ '/' + result.resultId.__str__()
        )

    else:
        surv_model = get_object_or_404(SurvM, survId=survid)
        questionlist = QuestionM.objects.filter(survId=survid).order_by('orderNum')

        form = SurvForm()
        form.fields['survId'].initial = survid
        form.fields['questionNum'].initial = questionlist.count()

        surv = surv_model.__dict__
        surv['question_num'] = questionlist.count()
        question_arr = []
        for question in questionlist:
            question_details = {}

            anslist = AnsM.objects.filter(survId=survid, questionId=question.questionId).order_by('questionId', 'orderNum')

            question_details = question.__dict__

            ans_arr = []
            for ans in anslist:
                ans_arr.append(ans.__dict__)

            question_details['ans_arr'] = ans_arr
            
            # 템플릿에서 이거 더하는 법 모름
            question_details['next_questionId'] = question.questionId + 1

            question_arr.append(question_details)

        context = {
            'form': form,
            'surv': surv,
            'question_arr': question_arr,
        }
        return render(request, template_name, context)


def result_view(request,survid,resultid):
    template_name = 'survDjango/result.html'

    surv = get_object_or_404(SurvM, survId=survid)
    result = get_object_or_404(ResultM, resultId=resultid)
    form = SurvForm()

    rank = ResultM.objects.filter(pointTop__gt=result.pointTop).aggregate(totalcnt=Sum('cnt'))
    #print(rank)
    rate = 0.0
    if rank['totalcnt'] :
        rate = (rank['totalcnt'].__int__() / surv.cnt) * 100
    else :
        rate = 0.01

    context = {
        'form': form,
        'surv': surv,
        'rank': rank,
        'rate': rate,
        'result': result,
    }

    return render(request, template_name, context)


def start_view(request,survid):
    template_name = 'survDjango/start.html'

    surv = get_object_or_404(SurvM, survId=survid)

    form = SurvForm()

    context = {
        'form': form,
        'surv': surv,
    }

    return render(request, template_name, context)


def index_view(request):
    return start_view(request,1)

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
#             #print(selectknight.username + selectknight.knightId.__str__() )
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