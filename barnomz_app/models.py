from django.db import models

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
)


class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    student_number = models.CharField(max_length=20, unique=True)
    major = models.CharField(max_length=100, choices=MAJOR_CHOICES)
    password = models.CharField(max_length=32)

    def create_user(self, username, student_number, major, password):
        self.username = username
        self.student_number = student_number
        self.major = major
        self.password = password
        self.save()

    def edit_user(self, username, student_number, major, password):
        self.refresh_from_db()
        self.username = username
        self.student_number = student_number
        self.major = major
        self.password = password
        self.save()


class Department(models.Model):
    name = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    code = models.CharField(max_length=10, unique=True)


class Professor(models.Model):
    full_name = models.CharField(max_length=255)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    rate = models.FloatField()
    knowledge_rate = models.FloatField()
    teaching_rate = models.FloatField()
    communication_rate = models.FloatField()
    exam_difficulty_rate = models.FloatField()
    number_of_votes = models.PositiveIntegerField()


class Course(models.Model):
    course_name = models.CharField(max_length=255)
    course_code = models.CharField(max_length=20, unique=True)
    unit_count = models.PositiveIntegerField()
    offered_by = models.ForeignKey('Professor', on_delete=models.CASCADE)
    group = models.PositiveIntegerField()
    day_of_week = models.CharField(max_length=10, choices=DAY_OF_WEEK_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    final_exam_date = models.DateTimeField()
    number_of_petitioners = models.PositiveIntegerField()
    number_of_capacity = models.PositiveIntegerField()
    number_of_enrolled = models.PositiveIntegerField()
    session = models.ForeignKey('ClassSession', on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)
    prerequisite = models.ForeignKey('Course', on_delete=models.SET_NULL, null=True)

    def add_new_course(self, course_name, course_code, unit_count, offered_by, group, day_of_week, start_time,
                       end_time, location, final_exam_date, number_of_Petitioners, number_of_capacity,
                       number_of_enrolled, professor, session, department, prerequisite):
        self.course_name = course_name
        self.course_code = course_code
        self.unit_count = unit_count
        self.offered_by = offered_by
        self.group = group
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.final_exam_date = final_exam_date
        self.number_of_petitioners = number_of_Petitioners
        self.number_of_capacity = number_of_capacity
        self.number_of_enrolled = number_of_enrolled
        self.professor = professor
        self.session = session
        self.department = department
        self.prerequisite = prerequisite
        self.save()


class ClassSession(models.Model):
    course_session = models.ForeignKey('Course', on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=DAY_OF_WEEK_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def make_custom_session(self, course, day_of_week, start_time, end_time, location):
        self.course_session = course
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.save()


class Schedule(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    classes = models.ManyToManyField('ClassSession')
    status = models.CharField(max_length=10, choices=[('public', 'Public'), ('private', 'Private')])
    is_default = models.BooleanField()

    def add_new_schedule(self, user, name, classes, status, is_default):
        self.user = user
        self.name = name
        self.classes = classes
        self.status = status
        self.is_default = is_default
        self.save()

    def make_default(self):
        self.is_default = True
        self.save()


class CommentOnProfessors(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    professor = models.ForeignKey('Professor', on_delete=models.CASCADE)
    text = models.TextField()
    rate = models.FloatField()
    knowledge_rate = models.FloatField()
    teaching_rate = models.FloatField()
    communication_rate = models.FloatField()
    exam_difficulty_rate = models.FloatField()
    date = models.DateTimeField()
    is_anonymous = models.BooleanField()
    is_deleted = models.BooleanField()

    def add_new_comment(self, user, course, professor, text, rate, knowledge_rate, teaching_rate, communication_rate,
                        exam_difficulty_rate, date, is_anonymous, is_deleted):
        self.user = user
        self.course = course
        self.professor = professor
        self.text = text
        self.rate = rate
        self.knowledge_rate = knowledge_rate
        self.teaching_rate = teaching_rate
        self.communication_rate = communication_rate
        self.exam_difficulty_rate = exam_difficulty_rate
        self.date = date
        self.is_anonymous = is_anonymous
        self.is_deleted = is_deleted
        self.save()

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()
