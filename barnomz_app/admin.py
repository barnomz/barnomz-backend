from django.contrib import admin
from .models import Student, Department, Professor, Course, Classroom, Schedule


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'student_number', 'major', 'enrollment_year')
    search_fields = ('first_name', 'last_name', 'student_number')
    list_filter = ('major', 'enrollment_year')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'head_of_department')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'staff_number', 'hiring_date', 'department')
    search_fields = ('first_name', 'last_name', 'staff_number')
    list_filter = ('department', 'hiring_date')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'course_code', 'unit_count', 'offered_by')
    search_fields = ('course_name', 'course_code')
    list_filter = ('offered_by',)


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = (
        'building', 'class_number', 'capacity', 'projector_available', 'whiteboard_available', 'wheelchair_accessible')
    search_fields = ('building', 'class_number')
    list_filter = ('projector_available', 'whiteboard_available', 'wheelchair_accessible')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('course', 'professor', 'day_of_week', 'start_time', 'end_time', 'location')
    search_fields = ('course__course_name', 'professor__first_name', 'professor__last_name')
    list_filter = ('day_of_week', 'professor', 'course')
