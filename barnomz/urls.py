from django.contrib import admin
from django.urls import path
from barnomz_app import views
from barnomz_app.views import ScheduleList

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/register/', views.register, name='api_register'),
    path('api/login/', views.login, name='api_login'),
    path('api/logout/', views.logout, name='api_logout'),
    path('api/schedules/', ScheduleList.as_view(), name='schedule_list'),
]
