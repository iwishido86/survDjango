# models.py
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from sympy import true


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=False, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class SurvM(models.Model):
    survId = models.IntegerField(default=0, help_text="설문번호",unique=True)
    title = models.CharField(max_length=100)
    survType = models.CharField(default='01',max_length=20)
    content = models.TextField()
    content2 = models.TextField()
    content3 = models.TextField()
    imgFile = models.CharField(default='N',max_length=100)
    iconImgFile = models.CharField(default='N', max_length=100)
    linkUrl = models.CharField(default='N',max_length=100)
    addScript = models.CharField(default='N', max_length=200)
    completeYn = models.CharField(default='N', max_length=1)
    pageNum = models.IntegerField(default=0, help_text="설문번호")
    deleteYn = models.CharField(default='N', max_length=1)
    orderNum = models.IntegerField(default=0, help_text="정렬순서")
    cnt = models.IntegerField(default=0, help_text="검사건수")



class QuestionM(models.Model):
    survId = models.IntegerField(default=0, help_text="설문번호")
    questionId = models.IntegerField(default=0, help_text="질문번호")
    title = models.CharField(max_length=100)
    questionType = models.CharField(default='01',max_length=2)
    content = models.TextField()
    content2 = models.TextField(default='',blank=True)
    imgFile = models.CharField(default='',blank=True, max_length=100)
    deleteYn = models.CharField(default='N', max_length=1)
    orderNum = models.IntegerField(default=0, help_text="정렬순서")


class AnsM(models.Model):
    survId = models.IntegerField(default=0, help_text="설문번호")
    questionId = models.IntegerField(default=0, help_text="질문번호")
    ansId = models.IntegerField(default=0, help_text="답변번호")
    content = models.TextField()
    point = models.IntegerField(default=0, help_text="질문점수")
    typeArr =   models.CharField(default='',max_length=50,blank=True)
    deleteYn = models.CharField(default='N', max_length=1)
    orderNum = models.IntegerField(default=0, help_text="정렬순서")


class ResultM(models.Model):
    survId = models.IntegerField(default=0, help_text="설문번호")
    resultId = models.IntegerField(default=0, help_text="결과번호")
    resultType = models.CharField(default='01', max_length=2)
    pointBottom = models.IntegerField(default=0, help_text="pointBottom")
    pointTop = models.IntegerField(default=0, help_text="pointTop")
    matchingPattern = models.CharField(default='',max_length=100,blank=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    content2 = models.TextField()
    content3 = models.TextField()
    imgFile = models.CharField(max_length=100)
    deleteYn = models.CharField(default='N', max_length=1)
    orderNum = models.IntegerField(default=0, help_text="정렬순서")
    cnt = models.IntegerField(default=0, help_text="검사건수")


class ResultHstoryL(models.Model):
    survId = models.IntegerField(default=0, help_text="설문번호")
    resultId = models.IntegerField(default=0, help_text="결과번호")
    content = models.CharField(max_length=300)
    content2 = models.CharField(default='N',max_length=300)
    content3 = models.CharField(default='N', max_length=300)
    createDate = models.DateTimeField(auto_now=True)


class ResultCommentL(models.Model):
    survId = models.IntegerField(default=0, help_text="설문번호")
    resultId = models.IntegerField(default=0, help_text="결과번호")
    content = models.CharField(max_length=300)
    content2 = models.CharField(default='N',max_length=300)
    passwd = models.CharField(default='N', max_length=300)
    likeCnt = models.IntegerField(default=0, help_text="좋아요순위")
    createDate = models.DateTimeField(auto_now=True)


class SymbolM(models.Model):
    SymbolId = models.AutoField(primary_key=True)
    SysMarketCd = models.CharField(max_length=100)
    Symbol = models.CharField(max_length=100)
    Market = models.CharField(max_length=100)
    Name = models.CharField(max_length=100)
    Sector = models.CharField(max_length=300,blank=True,null=True)
    ListingDate = models.DateTimeField(blank=True,null=True)
    SettleMonth = models.CharField(max_length=100,blank=True,null=True)
    Representative = models.CharField(max_length=100,blank=True,null=True)
    HomePage = models.CharField(max_length=100,blank=True,null=True)
    Region = models.CharField(max_length=100,blank=True,null=True)
    RefreshDate = models.DateTimeField(blank=True,null=True)
    AnalDate = models.DateTimeField(blank=True, null=True)
    createDate = models.DateTimeField(auto_now=True,blank=True)
    # 2581: {'Symbol': '238490', 'Market': 'KOSDAQ', 'Name': '힘스', 'Sector':
    # '특수 목적용 기계 제조업', 'Industry': 'OLED Mask 인장기, OLED Mask 검사기 등', 'ListingDate': Timestamp('2017-07-20
    #  00:00:00'), 'SettleMonth': '12월', 'Representative': '김주환', 'HomePage': 'http://www.hims.co.kr', 'Region': '인천
    # 광역시'


class CandleL(models.Model):
    CandleId = models.AutoField(primary_key=True)
    BaseDate = models.DateTimeField()
    Symbol = models.CharField(max_length=15)
    Open = models.FloatField(blank=True, null=True)
    High = models.FloatField(blank=True, null=True)
    Low = models.FloatField(blank=True, null=True)
    Close = models.FloatField(blank=True, null=True)
    Volume = models.FloatField(blank=True, null=True)
    Change = models.FloatField(default=0,blank=True, null=True)
    Content1 = models.FloatField(default=0)
    Content2 = models.FloatField(default=0)
    Content3 = models.CharField(max_length=60, blank=True, null=True)
    Content4 = models.CharField(max_length=60, blank=True, null=True)
    Content5 = models.CharField(max_length=60, blank=True, null=True)
    Content6 = models.CharField(max_length=60, blank=True, null=True)
    # {'Open': 15850.0, 'High': 15850.0, 'Low': 15350.0, 'Close': 15350.0, 'Volume': 18616.0, 'Change': -0.025396825396825418}


class SimCandleL(models.Model):
    BaseDate = models.DateTimeField()
    Symbol = models.CharField(max_length=15)
    SimBaseDate = models.DateTimeField()
    SimSymbol = models.CharField(max_length=15)
    SimTypeCd = models.CharField(max_length=2, help_text="유사유형:01:단기차트:02:추세")
    ChartNum = models.FloatField(default=0, help_text="수정주가대수")
    Content1 = models.FloatField(default=0, help_text="단기수익률")
    Content2 = models.FloatField(default=0, help_text="장기수익률")
    Content3 = models.FloatField(default=0)
    Content4 = models.FloatField(default=0)
    Content5 = models.CharField(max_length=100, blank=True, null=True)
    Content6 = models.CharField(max_length=100, blank=True, null=True)


class AnalDateM(models.Model):
    AnalDate = models.DateTimeField(blank=True, null=True)


class SimContentL(models.Model):
    AnalDate = models.DateTimeField()
    SimTypeCd = models.CharField(max_length=2, help_text="유사유형:01:Content3:02:Content4:03:안함:04:없음")
    Content = models.CharField(max_length=100, blank=True, null=True)
    SimSymbolCnt = models.FloatField(default=0, help_text="갯수")
    Content1 = models.FloatField(default=0, help_text="단기수익률")
    Content2 = models.FloatField(default=0, help_text="장기수익률")
    Content3 = models.CharField(max_length=100, blank=True, null=True)
    Content4 = models.CharField(max_length=100, blank=True, null=True)


class RecoSymbolL(models.Model):
    AnalDate = models.DateTimeField()
    Symbol = models.CharField(max_length=15)
    RecoTypeCd = models.CharField(max_length=2, help_text="유사유형:01:단기차트:02:추세")
    SimSymbolCnt = models.FloatField(default=0, help_text="갯수")
    Content1 = models.FloatField(default=0, help_text="단기수익률")
    Content2 = models.FloatField(default=0, help_text="장기수익률")
    Content3 = models.CharField(max_length=100, blank=True, null=True)
    Content4 = models.CharField(max_length=100, blank=True, null=True)
    RecoDispYn = models.CharField(max_length=2, blank=True, null=True, help_text="추천여부")
    Close = models.FloatField(default=0, help_text="종가")
    NowClose = models.FloatField(default=0, help_text="최근종가")


class RecoCandleL(models.Model):
    CandleId = models.AutoField(primary_key=True)
    BaseDate = models.DateTimeField()
    Symbol = models.CharField(max_length=15)
    Open = models.FloatField(blank=True, null=True)
    High = models.FloatField(blank=True, null=True)
    Low = models.FloatField(blank=True, null=True)
    Close = models.FloatField(blank=True, null=True)
    Volume = models.FloatField(blank=True, null=True)
    Change = models.FloatField(default=0,blank=True, null=True)
    Content1 = models.FloatField(default=0)
    Content2 = models.FloatField(default=0)
    Content3 = models.CharField(max_length=60, blank=True, null=True)
    Content4 = models.CharField(max_length=60, blank=True, null=True)
    Content5 = models.CharField(max_length=60, blank=True, null=True)
    Content6 = models.CharField(max_length=60, blank=True, null=True)
