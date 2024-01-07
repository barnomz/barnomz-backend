from django.contrib import admin
from django.urls import path
from barnomz_app.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/register/', register, name='api_register'),
    path('api/login/', login, name='api_login'),
    path('api/logout/', logout, name='api_logout'),
    path('api/schedules/', ScheduleList.as_view(), name='schedule_list'),
    path('api/schedules/', ScheduleList.as_view(), name='schedule_list'),
    path('api/schedules/', add_schedule, name='add_schedule'),
    path('api/schedules/<int:schedule_id>/', remove_schedule, name='remove_schedule'),
    path('api/schedules/<int:schedule_id>/course', add_course_to_schedule, name='add_course_to_schedule'),
    path('api/schedules/<int:schedule_id>/course', remove_course_from_schedule, name='remove_course_from_schedule'),
    path('api/schedules/<int:schedule_id>/makePublic', make_schedule_public, name='make_schedule_public'),
    path('api/schedules/<int:schedule_id>/duplicate', duplicate_schedule, name='duplicate_schedule'),
    path('departments', GetAllDepartments.as_view(), name='get_all_departments'),
    path('departments/<int:department_id>/courses', GetCoursesOfDepartment.as_view(), name='get_courses_of_department'),
    path('schedules/public', FilterPublicSchedules.as_view(), name='filter_public_schedules'),
    path('lecturers/<int:lecturer_id>', GetLecturerInfo.as_view(), name='get_lecturer_info'),
    path('lecturers/<int:lecturer_id>/reviews', GetAllReviewsAboutLecturer.as_view(),
         name='get_all_reviews_about_lecturer'),
    path('comments/add/', AddComment.as_view(), name='add_comment'),
    path('comments/remove/<int:comment_id>/', RemoveComment.as_view(), name='remove_comment'),
]
