from django.contrib import admin
from django.urls import path
from barnomz_app import views
from barnomz_app.views import ScheduleList, add_schedule, remove_schedule, add_course_to_schedule, \
    remove_course_from_schedule, make_schedule_public, duplicate_schedule

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/register/', views.register, name='api_register'),
    path('api/login/', views.login, name='api_login'),
    path('api/logout/', views.logout, name='api_logout'),
    path('api/schedules/', ScheduleList.as_view(), name='schedule_list'),
    path('api/schedules/', ScheduleList.as_view(), name='schedule_list'),
    path('api/schedules/', add_schedule, name='add_schedule'),
    path('api/schedules/<int:schedule_id>/', remove_schedule, name='remove_schedule'),
    path('api/schedules/<int:schedule_id>/course', add_course_to_schedule, name='add_course_to_schedule'),
    path('api/schedules/<int:schedule_id>/course', remove_course_from_schedule, name='remove_course_from_schedule'),
    path('api/schedules/<int:schedule_id>/makePublic', make_schedule_public, name='make_schedule_public'),
    path('api/schedules/<int:schedule_id>/duplicate', duplicate_schedule, name='duplicate_schedule'),
]
