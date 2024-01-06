from django.contrib import admin
from django.urls import path
from barnomz_app import views
from barnomz_app.views import ScheduleList, add_schedule, remove_schedule

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/register/', views.register, name='api_register'),
    path('api/login/', views.login, name='api_login'),
    path('api/logout/', views.logout, name='api_logout'),
    path('api/schedules/', ScheduleList.as_view(), name='schedule_list'),
    path('api/schedules/', ScheduleList.as_view(), name='schedule_list'),
    path('api/schedules/', add_schedule, name='add_schedule'),
    path('api/schedules/<int:schedule_id>/', remove_schedule, name='remove_schedule'),
]
