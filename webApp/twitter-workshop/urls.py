"""twitter-workshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, include
from django.contrib import admin
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', include('django.contrib.auth.urls')),

    path('app/home/', views.home, name='app/home'),
    path('app/query/', views.query, name='app/query'),
    path('app/database/', views.database, name='app/database'),
    path('app/dataset/', views.dataset, name='app/dataset'),
    path('app/interactions/', views.interactions, name='app/interactions'),
    # Ajax calls
    path('app/update_interactions/', views.update_interactions, name='app/update_interactions'),
    path('app/get_user_details/', views.get_user_details, name='app/get_user_details'),

    #temp
    path('app/update_queries/', views.update_queries, name='app/update_queries'),
]