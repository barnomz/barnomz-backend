from django.contrib import admin
from .models import *
import subprocess

admin.site.register(User)
admin.site.register(Department)
admin.site.register(Professor)
admin.site.register(ClassSession)
admin.site.register(Schedule)
admin.site.register(CommentOnProfessors)

def fetch_courses(modeladmin, request, queryset):
    script_path = './edu/main.go'
    command = f'go run {script_path}'

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        modeladmin.message_user(request, f'Script executed successfully: {output}')
    except subprocess.CalledProcessError as e:
        modeladmin.message_user(request, f'Error executing script: {e.output}', level='error')

fetch_courses.short_description = "Fetch courses"

class FetchCoursesModelAdmin(admin.ModelAdmin):
    actions = [fetch_courses]

admin.site.register(Course, FetchCoursesModelAdmin)
