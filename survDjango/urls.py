"""survjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token

from survDjango.chart_views import chart_index_view, chart_reco_view, chart_disp_view, chart_index_admin_view, \
    chart_list_view, chart_manual_view, dev_note_view, chart_reco2_view
from survDjango.views import surv_view, result_view, start_view, index_view
from survDjango.sym_views import ca_init_view, sym_bulk_view, \
    sym_reupdate_view, sym_index_view, sym_day_update_view, sym_anal2_view, sym_anal3_view, sym_anal4_view, \
    sym_reco_view, sym_reco_update_view, sym_prorate_update_view, sym_reco_cancel_view, sym_day_update2_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('start/<int:survid>/', start_view, name='start_view'), # 추가
    path('surv/<int:survid>/', surv_view, name='surv_view'), # 추가
    path('result/<int:survid>/<int:resultid>', result_view, name='result_view'), # 추가
    path('', index_view , name='index_view'), # 추가
    #주식차트분석
    path('symbol/', sym_index_view, name='sym_index_view'), # 추가
    path('anal_init/<str:sysmarketcd>', ca_init_view, name='ca_init_view'), # 추가
    path('symbol/bulk/<str:sysmarketcd>/<str:symbol>', sym_bulk_view, name='sym_bulk_view'), # 추가
    path('symbol/day_update/<str:sysmarketcd>/<str:basedate>', sym_day_update_view, name='sym_day_update_view'), # 추가
    path('symbol/day_update2/<str:sysmarketcd>/<str:basedate>', sym_day_update2_view, name='sym_day_update2_view'), # 추가
    path('symbol/anal2/<str:sysmarketcd>/<str:analdate>', sym_anal2_view, name='sym_anal2_view'), # 추가
    path('symbol/anal3/<str:sysmarketcd>/<str:analdate>', sym_anal3_view, name='sym_anal3_view'), # 추가
    path('symbol/anal4/<str:sysmarketcd>/<str:analdate>', sym_anal4_view, name='sym_anal4_view'),  # 추가
    path('symbol/reco/<str:sysmarketcd>/<str:symbol>', sym_reco_view, name='sym_reco_view'),  # 추가
    path('symbol/reupdate/<str:sysmarketcd>/<str:symbol>', sym_reupdate_view, name='sym_reupdate_view'), # 추가
    path('symbol/reco_update/<str:sysmarketcd>/<str:symbol>', sym_reco_update_view, name='sym_reco_update_view'), # 추가
    path('symbol/reco_cancel/<str:sysmarketcd>/<str:symbol>', sym_reco_cancel_view, name='sym_reco_cancel_view'), # 추가
    path('symbol/prorate_update/<str:sysmarketcd>/<str:analdate>/<str:symbol>', sym_prorate_update_view, name='sym_prorate_update_view'), # 추가

    #주식차트고객
    path('chart/', chart_index_view, name='chart_index_view'),  # 추가
    path('chart/manage/', chart_index_admin_view, name='chart_index_admin_view'),  # 추가
    path('chart/list/', chart_list_view, name='chart_list_view'),  # 추가
    path('chart/manual/', chart_manual_view, name='chart_manual_view'),  # 추가
    path('chart/reco/<str:sysmarketcd>/<str:symbol>', chart_reco_view, name='chart_reco_view'),  # 추가
    path('chart/reco2/<str:sysmarketcd>/<str:symbol>', chart_reco2_view, name='chart_reco2_view'),  # 추가
    path('chart/disp/<str:sysmarketcd>/<str:symbol>', chart_disp_view, name='chart_disp_view'),  # 추가

    #개발자노트
    path('devnote/', dev_note_view, name='dev_note_view'),  # 추가

    ]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
