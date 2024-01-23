from django.contrib import admin
from django.urls import path, include

from barnomz_app.views import register, login, logout, ScheduleList, add_schedule, remove_schedule, \
    add_course_to_schedule, remove_course_from_schedule, make_schedule_public, duplicate_schedule, GetAllDepartments, \
    GetCoursesOfDepartment, FilterPublicSchedules, GetLecturerInfo, GetAllReviewsAboutLecturer, AddComment, \
    RemoveComment, like_comment, dislike_comment

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/auth/register/', register, name='api_register'),
    path('api/auth/login/', login, name='api_login'),
    path('api/auth/logout/', logout, name='api_logout'),
    path('api/schedules/', ScheduleList.as_view(), name='schedule_list'),
    path('api/schedules/', add_schedule, name='add_schedule'),
    path('api/schedules/<int:schedule_id>/', remove_schedule, name='remove_schedule'),
    path('api/schedules/<int:schedule_id>/course', add_course_to_schedule, name='add_course_to_schedule'),
    path('api/schedules/<int:schedule_id>/course', remove_course_from_schedule, name='remove_course_from_schedule'),
    path('api/schedules/<int:schedule_id>/makePublic', make_schedule_public, name='make_schedule_public'),
    path('api/schedules/<int:schedule_id>/duplicate', duplicate_schedule, name='duplicate_schedule'),
    path('api/departments', GetAllDepartments.as_view(), name='get_all_departments'),
    path('api/departments/<int:department_id>/courses', GetCoursesOfDepartment.as_view(), name='get_courses_of_department'),
    path('api/schedules/public', FilterPublicSchedules.as_view(), name='filter_public_schedules'),
    path('api/lecturers/<int:lecturer_id>', GetLecturerInfo.as_view(), name='get_lecturer_info'),
    path('api/lecturers/<int:lecturer_id>/reviews', GetAllReviewsAboutLecturer.as_view(),
         name='get_all_reviews_about_lecturer'),
    path('api/comments/add/', AddComment.as_view(), name='add_comment'),
    path('api/comments/remove/<int:comment_id>/', RemoveComment.as_view(), name='remove_comment'),
    path('captcha/', include('captcha.urls')),
    path('comments/<int:comment_id>/like/', like_comment, name='like_comment'),
    path('comments/<int:comment_id>/dislike/', dislike_comment, name='dislike_comment')
]
