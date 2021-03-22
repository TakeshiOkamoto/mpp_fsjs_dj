"""mpp_fsjs_dj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
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
from django.urls import path, include

urlpatterns = [

    # この管理ツールは本稼働時は削除すること
    path('admin/', admin.site.urls),
    
    path('', include('fsjs_main.urls')),
    path('journals/', include('fsjs_journals.urls')),
    path('capitals/', include('fsjs_capitals.urls')),
    path('accounts/', include('fsjs_accounts.urls')),
    path('login/', include('fsjs_login.urls')),    
]
