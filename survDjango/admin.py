from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Count

from .models import SurvM, QuestionM, AnsM, ResultM, \
    ResultHstoryL  # 추가

# Register your models here.


class SurvMAdmin(admin.ModelAdmin):
    list_display = ('survId', 'title', 'survType' ,'imgFile', 'orderNum',)


class QuestionMAdmin(admin.ModelAdmin):
    list_display = ('survId', 'questionId', 'content', 'orderNum', 'questionType',)


class AnsMAdmin(admin.ModelAdmin):
    list_display = ('survId', 'questionId', 'ansId','content', 'point',)


class ResultMAdmin(admin.ModelAdmin):
    list_display = ('survId', 'resultId', 'pointBottom', 'pointTop', 'title', 'imgFile',)


class ResultHstoryLAdmin(admin.ModelAdmin):
    list_display = ('survId', 'resultId', 'content', 'content2', 'content3', 'createDate',)



admin.site.register(SurvM,SurvMAdmin)  # 추가
admin.site.register(QuestionM,QuestionMAdmin)  # 추가
admin.site.register(AnsM,AnsMAdmin)  # 추가
admin.site.register(ResultHstoryL,ResultHstoryLAdmin)  # 추가
admin.site.register(ResultM, ResultMAdmin)