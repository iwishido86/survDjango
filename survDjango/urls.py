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

from survDjango.chart_views import dev_note_view
from survDjango.views import surv_view, result_view, start_view, index_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('start/<int:survid>/', start_view, name='start_view'), # 추가
    path('surv/<int:survid>/', surv_view, name='surv_view'), # 추가
    path('result/<int:survid>/<int:resultid>', result_view, name='result_view'), # 추가
    path('', index_view , name='index_view'), # 추가


    #개발자노트
    path('devnote/', dev_note_view, name='dev_note_view'),  # 추가

    ]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
