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
                #logger.info(request.POST.get('radio'+i.__str__(), ''))
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
                # logger.info(request.POST.get('radio'+i.__str__(), ''))
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
            #logger.info(typeArr)
            for typeInt in typeArr:
                if typeInt > 0:
                    typeStr = typeStr + "1"
                else:
                    typeStr = typeStr + "0"

            historyContent = historyContent + ":::" + typeArr.__str__()
            historyContent2 = typeStr
            #logger.info(historyContent)
            #logger.info(historyContent2)
            # 여기 튜닝 원쿼리로
            result = get_object_or_404(ResultM, survId=survid, matchingPattern=typeStr)
            result.cnt = result.cnt + 1
            result.save()

        surv.cnt = surv.cnt + 1
        surv.save()

        request.session['completeYn'] = 'Y'
        # 내역 저장 - 속도,용량 맞추려고 당분간 아웃
        # resultHstoryL = ResultHstoryL.objects.create()
        #
        # resultHstoryL.survId = survId
        # resultHstoryL.resultId = result.resultId
        # resultHstoryL.content = historyContent
        # resultHstoryL.content2 = historyContent2
        #
        # resultHstoryL.save()


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
        if request.session['completeYn'] == 'Y':
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
        #logger.info(rank)

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

    survlist = SurvM.objects.order_by('-cnt')

    #resultHstoryL = ResultHstoryL.objects.all()
    #resultHstoryL.delete()

    context = {
        'survlist': survlist,
    }

    return render(request, template_name, context)
