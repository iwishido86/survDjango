from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Count

from .models import SurvM, QuestionM, AnsM, ResultM, \
    ResultHstoryL, ResultCommentL  # 추가

# Register your models here.


class SurvMAdmin(admin.ModelAdmin):
    list_display = ('survId', 'title', 'survType' ,'imgFile', 'orderNum',)
    list_filter = ('survId',)


class QuestionMAdmin(admin.ModelAdmin):
    list_display = ('survId', 'questionId', 'content', 'orderNum', 'questionType',)
    list_filter = ('survId',)
    search_fields = ('survId',)


class AnsMAdmin(admin.ModelAdmin):
    list_display = ('survId', 'questionId', 'ansId','content', 'point','typeArr')
    list_filter = ('survId', 'questionId',)
    search_fields = ('survId', 'questionId',)


class ResultMAdmin(admin.ModelAdmin):
    list_display = ('survId', 'resultId', 'pointBottom', 'pointTop', 'title', 'imgFile',)
    list_filter = ('survId', 'resultId',)
    search_fields = ('survId',)


class ResultHstoryLAdmin(admin.ModelAdmin):
    list_display = ('survId', 'resultId', 'content', 'content2', 'content3', 'createDate',)
    list_filter = ('survId', 'resultId',)
    search_fields = ('survId',)


class ResultCommentLAdmin(admin.ModelAdmin):
    list_display = ('survId', 'resultId', 'content', 'content2', 'likeCnt', 'createDate',)
    list_filter = ('survId', 'resultId',)
    search_fields = ('survId',)


admin.site.register(SurvM,SurvMAdmin)  # 추가
admin.site.register(QuestionM,QuestionMAdmin)  # 추가
admin.site.register(AnsM,AnsMAdmin)  # 추가
admin.site.register(ResultHstoryL,ResultHstoryLAdmin)  # 추가
admin.site.register(ResultM, ResultMAdmin)
admin.site.register(ResultCommentL, ResultCommentLAdmin)