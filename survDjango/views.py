from random import random, randint

from django.db.models import Q, Max
from django.forms import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .forms import UserLoginForm, SurvForm
from .models import SurvM, QuestionM, AnsM
from .serializers import RegistrationUserSerializer


def surv_view(request,survid):
    template_name = 'survDjango/surv.html'

    if request.method == 'POST':
        # form = KnightSelectForm(request.POST)
        #
        # username = request.POST.get('username')
        #
        # user, created = User.objects.get_or_create(
        #     username=username
        # )
        #
        # user.username = username
        # user.readyYn = 'Y'
        # user.joinYn = 'Y'
        #
        # user.save()
        #
        # delSelectKnightList = SelectKnight.objects.filter(username=username)
        #
        # delSelectKnightList.delete()
        #
        # knightliststr = request.POST.get('knightliststr')
        #
        # knightlist = knightliststr.split(';')
        #
        # for knightId in knightlist :
        #     if knightId == '':
        #         break
        #
        #     selectKnight, created = SelectKnight.objects.get_or_create(
        #         username=username,
        #         knightId=knightId
        #     )
        #     selectKnight.save()

        return HttpResponseRedirect(
            '/mycard/'
        )

    else:
        surv = get_object_or_404(SurvM, survId=survid)
        form = SurvForm()
        form.fields['survId'].initial = survid
        questionlist = QuestionM.objects.filter(survId=survid).order_by('orderNum')

        page_num = 0
        page_arr = []
        page_detail = {}
        question_arr = []
        for question in questionlist:
            question_details = {}

            anslist = AnsM.objects.filter(survId=survid, questionId=question.questionId).order_by('questionId', 'orderNum')

            question_details = question.__dict__

            ans_arr = []
            for ans in anslist:
                ans_arr.append(ans.__dict__)

            question_details['ans_arr'] = ans_arr

            question_arr.append(question_details)

            print(question.questionId % surv.pageNum)

            if question.questionId % surv.pageNum == 0 :
                page_num = page_num + 1
                page_detail = {}
                page_detail['page_num'] = page_num
                page_detail['question_arr'] = question_arr
                page_arr.append(page_detail)
                print(page_arr)
                question_arr = []

        #마지막
        if question_arr :
            page_num = page_num + 1
            page_detail = {}
            page_detail['page_num'] = page_num
            page_detail['question_arr'] = question_arr
            page_arr.append(page_detail)

        # for question in questionlist:
        #     question["anslist"] = AnsM.objects.filter(survId=survid, questionId=question["questionId"]).order_by(
        #         'questionId', 'orderNum')
        #
        # anslist = AnsM.objects.filter(survId=survid).order_by('questionId', 'orderNum')

        context = {
            'form': form,
            'surv': surv,
            'last_page_num': page_num,
            'page_arr': page_arr,
        }
        return render(request, template_name, context)



def result_view(request,survid):
    template_name = 'survDjango/surv.html'


    surv = get_object_or_404(SurvM, survId=survid)
    form = SurvForm()
    form.fields['survid'].initial = survid
    questionlist = QuestionM.objects.filter(survId=survid).order_by('orderNum')

    for question in questionlist:
        question["anslist"] = AnsM.objects.filter(survId=survid,questionId =question["questionId"]).order_by('questionId','orderNum')

    anslist = AnsM.objects.filter(survId=survid).order_by('questionId','orderNum')

    context = {
        'form': form,
        'survid':survid,
        'questionlist': questionlist,
        'anslist' : anslist,
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