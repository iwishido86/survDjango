from django.contrib import admin

from .models import SurvM, QuestionM, AnsM, ResultM, \
    ResultHstoryL  # 추가

# Register your models here.

admin.site.register(SurvM)  # 추가
admin.site.register(QuestionM)  # 추가
admin.site.register(AnsM)  # 추가
admin.site.register(ResultM)  # 추가
admin.site.register(ResultHstoryL)  # 추가

