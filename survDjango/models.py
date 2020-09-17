# models.py
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


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
    content2 = models.TextField(default='')
    imgFile = models.CharField(default='', max_length=100)
    deleteYn = models.CharField(default='N', max_length=1)
    orderNum = models.IntegerField(default=0, help_text="정렬순서")


class AnsM(models.Model):
    survId = models.IntegerField(default=0, help_text="설문번호")
    questionId = models.IntegerField(default=0, help_text="질문번호")
    ansId = models.IntegerField(default=0, help_text="답변번호")
    content = models.TextField()
    point = models.IntegerField(default=0, help_text="질문점수")
    typeArr =   models.CharField(default='',max_length=50)
    deleteYn = models.CharField(default='N', max_length=1)
    orderNum = models.IntegerField(default=0, help_text="정렬순서")


class ResultM(models.Model):
    survId = models.IntegerField(default=0, help_text="설문번호")
    resultId = models.IntegerField(default=0, help_text="결과번호")
    resultType = models.CharField(default='01', max_length=2)
    pointBottom = models.IntegerField(default=0, help_text="pointBottom")
    pointTop = models.IntegerField(default=0, help_text="pointTop")
    matchingPattern = models.CharField(default='',max_length=100)
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


