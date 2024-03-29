import uuid
from datetime import datetime, time
import gettext

gettext.install('barnomz', localedir=None)
_ = gettext.gettext
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.conf import settings
from django.utils import timezone

MAJOR_CHOICES = (
    ('CE', 'Computer Engineering'), ('CS', 'Computer Science'),
    ('EE', 'Electrical Engineering'), ('MSE', 'Material Science Engineering'),
    ('AE', 'Aerospace Engineering'), ('ME', 'Mechanical Engineering'),
    ('CHE', 'Chemical Engineering'), ('IE', 'Industrial Engineering'),
    ('AM', 'Applied Mathematics'), ('P', 'Physics'), ('E', 'Economics')
)

DEPARTMENT_CHOICES = (
    ('CE', 'Computer Engineering'), ('EE', 'Electrical Engineering'),
    ('MSE', 'Material Science Engineering'), ('AE', 'Aerospace Engineering'),
    ('ME', 'Mechanical Engineering'), ('CHE', 'Chemical Engineering'),
    ('IE', 'Industrial Engineering'), ('MS', 'Mathematical Science'),
    ('P', 'Physics'), ('E', 'Economics')
)

DAY_OF_WEEK_CHOICES = (
    ('Saturday', 'Saturday'), ('Sunday', 'Sunday'), ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'),
    # ('SatMon', 'Saturday and Monday'), ('SunTue', 'Sunday and Tuesday'),
)

GRADE_CHOICES = (
    ('Bsc', 'کارشناسی'),
    ('Msc', 'کارشناسی-ارشد')
)

STRICTNESS_CHOICES = {
    ('strict', 'پیشنیاز'),
    ('loose', 'هنمیاز')
}


class User(AbstractUser, PermissionsMixin):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    student_number = models.CharField(max_length=20, unique=True)
    major = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    is_staff = models.BooleanField(default=False, blank=True, null=True)
    last_login = models.DateTimeField(_('last login'), blank=True, null=True, default=timezone.now)

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
    )


class Department(models.Model):
    name = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    code = models.CharField(max_length=10)  # temporarily remove unique condition

    def fill(self, name, code):
        self.name = name
        self.code = code
        self.save()


class Professor(models.Model):
    full_name = models.CharField(max_length=255)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    rate = models.FloatField()
    knowledge_rate = models.FloatField()
    teaching_rate = models.FloatField()
    communication_rate = models.FloatField()
    exam_difficulty_rate = models.FloatField()
    number_of_votes = models.PositiveIntegerField()

    def fill(self, full_name, department):
        self.full_name = full_name
        self.department = department
        self.rate = 0
        self.knowledge_rate = 0
        self.teaching_rate = 0
        self.communication_rate = 0
        self.exam_difficulty_rate = 0
        self.number_of_votes = 0
        self.save()


class Course(models.Model):
    course_name = models.CharField(max_length=255)
    course_code = models.CharField(max_length=20, unique=True)
    unit_count = models.PositiveIntegerField()
    presented_by = models.ForeignKey('Professor', on_delete=models.CASCADE)
    group = models.PositiveIntegerField()
    location = models.ForeignKey('Classroom', null=True, on_delete=models.SET_NULL)
    final_exam_date = models.CharField(max_length=64)
    final_exam_time = models.TimeField(default=time(9, 0))
    number_of_petitioners = models.PositiveIntegerField()
    number_of_capacity = models.PositiveIntegerField()
    number_of_enrolled = models.PositiveIntegerField()
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)
    info = models.CharField(max_length=512, default="")
    prerequisite_text = models.CharField(max_length=255, default="")
    warning = models.CharField(max_length=512, default="")
    grade = models.CharField(max_length=32, choices=GRADE_CHOICES, default="Bsc")

    def add_new_course(self, course_name, course_code, unit_count, presented_by, group,
                       location, final_exam_date, final_exam_time, number_of_Petitioners,
                       number_of_capacity, number_of_enrolled, department, info, warning, grade):
        self.course_name = course_name
        self.course_code = course_code
        self.unit_count = unit_count
        self.presented_by = presented_by
        self.group = group
        self.location = location
        self.final_exam_date = final_exam_date
        self.final_exam_time = final_exam_time
        self.number_of_petitioners = number_of_Petitioners
        self.number_of_capacity = number_of_capacity
        self.number_of_enrolled = number_of_enrolled
        self.department = department
        self.info = info
        self.warning = warning
        self.group = group
        self.save()

    def fill(self, course_name, course_code, unit_count, presented_by, group,
             location, final_exam_date, final_exam_time, number_of_capacity,
             number_of_enrolled, department, info, warning, grade):
        self.course_name = course_name
        self.course_code = course_code
        self.unit_count = unit_count
        self.presented_by = presented_by
        self.group = group
        self.location = location
        self.final_exam_date = final_exam_date
        self.final_exam_time = final_exam_time
        self.number_of_petitioners = 0
        self.number_of_capacity = number_of_capacity
        self.number_of_enrolled = number_of_enrolled
        self.department = department
        self.info = info
        self.warning = warning
        self.group = group
        self.save()


class Classroom(models.Model):
    building = models.CharField(max_length=64)
    class_name = models.CharField(max_length=128)

    def fill(self, building, class_name):
        self.building = building
        self.class_name = class_name
        self.save()


class ClassSession(models.Model):
    course_session = models.ForeignKey('Course', on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=DAY_OF_WEEK_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.ForeignKey('Classroom', on_delete=models.SET_NULL, null=True)

    def make_custom_session(self, course, day_of_week, start_time, end_time, location):
        self.course_session = course
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.save()

    def fill(self, course, day_of_week, start_time, end_time, location):
        self.course_session = course
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.save()


class Schedule(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    classes = models.ManyToManyField('ClassSession', blank=True)
    status = models.CharField(max_length=10, choices=[('public', 'Public'), ('private', 'Private')], default='private')

    def add_new_schedule(self, user):
        self.user = user
        self.classes = []
        self.save()

    def fill(self, user, classes, status):
        self.user = user
        self.classes = classes
        self.status = status
        self.save()


class CommentOnProfessors(models.Model):
    professor = models.ForeignKey('Professor', on_delete=models.CASCADE)
    text = models.TextField()
    rate = models.FloatField(null=True, blank=True)
    knowledge_rate = models.FloatField(null=True, blank=True)
    teaching_rate = models.FloatField(null=True, blank=True)
    communication_rate = models.FloatField(null=True, blank=True)
    exam_difficulty_rate = models.FloatField(null=True, blank=True)
    is_anonymous = models.BooleanField(default=True,null=True)
    is_deleted = models.BooleanField(default=False, null=True)

    def count_likes(self):
        return CommentLike.objects.filter(comment=self, like=True).count()

    def count_dislikes(self):
        return CommentLike.objects.filter(comment=self, like=False).count()

    def add_new_comment(self, professor, text, rate, knowledge_rate, teaching_rate, communication_rate,
                        exam_difficulty_rate, is_anonymous, is_deleted):
        self.professor = professor
        self.text = text
        self.rate = rate
        self.knowledge_rate = knowledge_rate
        self.teaching_rate = teaching_rate
        self.communication_rate = communication_rate
        self.exam_difficulty_rate = exam_difficulty_rate
        self.is_anonymous = is_anonymous
        self.is_deleted = is_deleted
        self.save()

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    def fill(self, professor, text, rate, knowledge_rate, teaching_rate, communication_rate,
             exam_difficulty_rate, is_anonymous, is_deleted):
        self.professor = professor
        self.text = text
        self.rate = rate
        self.knowledge_rate = knowledge_rate
        self.teaching_rate = teaching_rate
        self.communication_rate = communication_rate
        self.exam_difficulty_rate = exam_difficulty_rate
        self.is_anonymous = is_anonymous
        self.is_deleted = is_deleted
        self.save()


class CommentLike(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    comment = models.ForeignKey('CommentOnProfessors', on_delete=models.CASCADE)
    like = models.BooleanField()

    class Meta:
        unique_together = ('user', 'comment')
