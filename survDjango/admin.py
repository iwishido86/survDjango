from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Count

from .models import SurvM, QuestionM, AnsM, ResultM, \
    ResultHstoryL, ResultCommentL, SymbolM, CandleL, SimCandleL, SimContentL, RecoSymbolL, RecoCandleL, AnalDateM, \
    AnalMasterH  # 추가

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


class SymbolMAdmin(admin.ModelAdmin):
    list_display = ('SymbolId', 'SysMarketCd', 'Symbol', 'Market', 'Name', 'Sector',)
    list_filter = ( 'SysMarketCd',)
    search_fields = ('SysMarketCd', 'Symbol', 'Market',  'Name',)


class CandleLAdmin(admin.ModelAdmin):
    list_display = ('BaseDate', 'Symbol', 'Open', 'High', 'Low' ,'Close','Volume','Content3',)
    list_filter = ( 'BaseDate',)
    search_fields = ( 'BaseDate','Symbol','Content3',)


class SimCandleLAdmin(admin.ModelAdmin):
    list_display = ('BaseDate', 'Symbol', 'SimBaseDate', 'SimSymbol', 'ChartNum' ,'Content1','Content2',)
    list_filter = ( 'BaseDate',)
    search_fields = ( 'BaseDate','Symbol',)


class SimContentLAdmin(admin.ModelAdmin):
    list_display = ('AnalDate', 'SimTypeCd', 'Content', 'SimSymbolCnt', 'Content1' ,'Content2','Content3',)
    list_filter = ('AnalDate',)
    search_fields = ('AnalDate','Content',)


class RecoSymbolLAdmin(admin.ModelAdmin):
    list_display = ('AnalDate', 'Symbol', 'RecoTypeCd', 'SimSymbolCnt', 'Content1', 'Content2', 'Content3', 'Content4', 'RecoDispYn', 'Close', 'NowClose', 'MaxClose','MaxHigh',)
    list_filter = ('AnalDate',)
    search_fields = ('AnalDate','Symbol',)


class RecoCandleLAdmin(admin.ModelAdmin):
    list_display = ('BaseDate', 'Symbol', 'Open', 'High', 'Low' ,'Close','Volume','Content3','Content4',)
    list_filter = ( 'BaseDate',)
    search_fields = ( 'BaseDate','Symbol','Content3',)

class AnalDateMAdmin(admin.ModelAdmin):
    list_display = ('AnalDate',)
    list_filter = ('AnalDate',)
    search_fields = ('AnalDate',)


class AnalMasterHAdmin(admin.ModelAdmin):
    list_display = ('AnalDate','AnalTypeCd','CompleteYn','createDate',)
    list_filter = ('AnalDate',)
    search_fields = ('AnalDate',)


admin.site.register(AnalMasterH,AnalMasterHAdmin)  # 추가
admin.site.register(AnalDateM,AnalDateMAdmin)  # 추가
admin.site.register(RecoSymbolL,RecoSymbolLAdmin)  # 추가
admin.site.register(RecoCandleL,RecoCandleLAdmin)  # 추가
admin.site.register(SimContentL,SimContentLAdmin)  # 추가
admin.site.register(SimCandleL,SimCandleLAdmin)  # 추가
admin.site.register(CandleL,CandleLAdmin)  # 추가
admin.site.register(SymbolM,SymbolMAdmin)  # 추가
admin.site.register(SurvM,SurvMAdmin)  # 추가
admin.site.register(QuestionM,QuestionMAdmin)  # 추가
admin.site.register(AnsM,AnsMAdmin)  # 추가
admin.site.register(ResultHstoryL,ResultHstoryLAdmin)  # 추가
admin.site.register(ResultM, ResultMAdmin)
admin.site.register(ResultCommentL, ResultCommentLAdmin)