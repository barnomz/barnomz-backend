from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Department)
admin.site.register(Professor)
admin.site.register(Course)
admin.site.register(ClassSession)
admin.site.register(Schedule)
admin.site.register(CommentOnProfessors)
