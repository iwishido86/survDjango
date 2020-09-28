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
from .models import SurvM, QuestionM, AnsM, ResultHstoryL, ResultM, ResultCommentL
from .serializers import RegistrationUserSerializer


def surv_view(request,survid):
    template_name = 'survDjango/surv.html'

    if request.method == 'POST':

        survId = request.POST.get('survId', '')
        questionNum = request.POST.get('questionNum', '')
        historyContent = ""
        historyContent2 = ""

        surv = get_object_or_404(SurvM, survId=survId)
        
        if surv.survType == '01' :          # 점수제
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

            historyContent2 = point.__str__()
            # 여기 튜닝 원쿼리로
            result = get_object_or_404(ResultM, survId=survid, pointBottom__lte=point, pointTop__gte=point)
            result.cnt = result.cnt + 1
            result.save()

        elif surv.survType == '02':  # 점수제
            # TODO 동적으로 바꾸자 지금은 4개만됨
            typeArr = [0,0,0,0]
            for i in range(1, int(questionNum) + 1):
                # print(request.POST.get('radio'+i.__str__(), ''))
                ansId = request.POST.get('radio' + i.__str__())

                # 여기 튜닝 원쿼리로
                ans = get_object_or_404(AnsM, survId=survid, questionId=i, ansId=ansId)

                #TODO for문 인덱스 모르겟다
                index = 0
                for j in ans.typeArr.split(','):
                    
                    typeArr[index] = typeArr[index] + int(j)
                    index = index + 1

                historyContent = historyContent + ansId + "-" + ans.typeArr.__str__() + ":"

            # 결과
            typeStr = ""
            #print(typeArr)
            for typeInt in typeArr:
                if typeInt > 0:
                    typeStr = typeStr + "1"
                else:
                    typeStr = typeStr + "0"

            historyContent = historyContent + ":::" + typeArr.__str__()
            historyContent2 = typeStr
            #print(historyContent)
            #print(historyContent2)
            # 여기 튜닝 원쿼리로
            result = get_object_or_404(ResultM, survId=survid, matchingPattern=typeStr)
            result.cnt = result.cnt + 1
            result.save()

        surv.cnt = surv.cnt + 1
        surv.save()

        request.session['completeYn'] = 'Y'
        # 내역 저장 - 속도,용량 맞추려고 당분간 아웃
        resultHstoryL = ResultHstoryL.objects.create()

        resultHstoryL.survId = survId
        resultHstoryL.resultId = result.resultId
        resultHstoryL.content = historyContent
        resultHstoryL.content2 = historyContent2

        resultHstoryL.save()


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

        anslist = AnsM.objects.filter(survId=survid,).order_by('questionId', 'orderNum')

        for question in questionlist:
            question_details = {}

            question_details = question.__dict__

            anslist2 = anslist.filter(survId=survid, questionId=question.questionId)

            ans_arr = []
            for ans in anslist2:
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
    if request.method == 'POST':
        resultComment = ResultCommentL.objects.create()

        resultComment.survId = survid
        resultComment.resultId = resultid
        resultComment.content = request.POST.get('comment', '')
        
        resultComment.save()
        #한번만 입력
        request.session['completeYn'] = 'N'

    template_name = 'survDjango/result'+survid.__str__()+'.html'

    surv = get_object_or_404(SurvM, survId=survid)
    result = get_object_or_404(ResultM, survId=survid, resultId=resultid)
    form = SurvForm()

    rate = 0.0
    if surv.survType == '01':  # 점수제
        rank = ResultM.objects.filter(survId=survid,pointTop__gt=result.pointTop).aggregate(totalcnt=Sum('cnt'))

        #rank = ResultM.objects.filter(survId=survid,resultId=resultid).aggregate(totalcnt=Sum('cnt'))
        #print(rank)

        if rank['totalcnt'] :
            rate = (rank['totalcnt'].__int__() / surv.cnt) * 100
        else :
            rate = 0.01
    elif surv.survType == '02':  # 타입
        rate = (result.cnt / surv.cnt) * 100

    commentlist = ResultCommentL.objects.filter(survId=survid, resultId=resultid).order_by('-createDate')[0:10]

    survlist = SurvM.objects.filter(~Q(survId=survid)).order_by('orderNum')

    context = {
        'form': form,
        'surv': surv,
        'rate': rate,
        'result': result,
        'survlist':survlist,
        'commentlist': commentlist,

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
    template_name = 'survDjango/index.html'

    survlist = SurvM.objects.order_by('orderNum')

    # resultHstoryL = ResultHstoryL.objects.all()
    # resultHstoryL.delete()

    context = {
        'survlist': survlist,
    }

    return render(request, template_name, context)

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