from django.utils.dateparse import parse_date, parse_time
from rest_framework import serializers

from barnomz_app.models import *


class CourseSerializer(serializers.ModelSerializer):
    presented_by = serializers.CharField(max_length=255)
    exam_date = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'course_name', 'course_code', 'unit_count', 'presented_by', 'group',
                  'exam_date', 'number_of_petitioners', 'number_of_capacity',
                  'number_of_enrolled', 'location', 'department', 'warning', 'grade', 'info']

    @staticmethod
    def get_exam_date(obj):
        exam_date_str = obj.final_exam_date
        if isinstance(exam_date_str, str):
            exam_date = parse_date(exam_date_str.replace('/', '-'))
        else:
            exam_date = exam_date_str

        exam_time_str = obj.final_exam_time
        if isinstance(exam_time_str, str):
            exam_time = parse_time(exam_time_str)
        else:
            exam_time = exam_time_str

        if exam_date and exam_time:
            formatted_date = exam_date.strftime('%Y-%m-%d')
            formatted_time = exam_time.strftime('%H:%M')
            exam_datetime = f'{formatted_date}T{formatted_time}'
            return exam_datetime
        return None

    def get_presented_by(self):
        return Professor.objects.get(self.presented_by).full_name


class ClassSessionSerializer(serializers.ModelSerializer):
    day_of_week = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = ClassSession
        fields = ['id', 'day_of_week', 'start_time', 'end_time', 'location']

    @staticmethod
    def get_day_of_week(obj):
        # Using the object instance to get the day_of_week attribute
        day_name = obj.day_of_week
        day_to_int = {
            'شنبه': 0,
            'یکشنبه': 1,
            'دوشنبه': 2,
            'سه-شنبه': 3,
            'چهارشنبه': 4,
            'پنجشنبه': 5,
            'جمعه': 6,
        }
        day_list = []
        if (day_to_int.get(day_name) == 3 or day_to_int.get(day_name) == 1) and obj.course_session.unit_count == 3:
            day_list.append(1)
            day_list.append(3)
        elif (day_to_int.get(day_name) == 0 or day_to_int.get(day_name) == 2) and obj.course_session.unit_count == 3:
            day_list.append(0)
            day_list.append(2)
        else:
            day_list.append(day_to_int.get(day_name))
        return day_list

    @staticmethod
    def get_start_time(obj):
        if obj.start_time is None:
            return None
        return obj.start_time.strftime('%H:%M')

    @staticmethod
    def get_end_time(obj):
        if obj.end_time is None:
            return None
        return obj.end_time.strftime('%H:%M')


class ClassSessionAllDataSerializer(ClassSessionSerializer):
    course_name = serializers.SerializerMethodField()
    course_code = serializers.SerializerMethodField()
    presented_by = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    unit_count = serializers.SerializerMethodField()
    exam_date = serializers.SerializerMethodField()

    class Meta(ClassSessionSerializer.Meta):
        fields = ClassSessionSerializer.Meta.fields + ['course_name', 'course_code', 'presented_by', 'group',
                                                       'unit_count', 'exam_date']

    @staticmethod
    def get_course_name(obj):
        return obj.course_session.course_name

    @staticmethod
    def get_course_code(obj):
        return obj.course_session.course_code

    @staticmethod
    def get_presented_by(obj):
        return obj.course_session.presented_by.full_name if obj.course_session.presented_by else None

    @staticmethod
    def get_group(obj):
        return obj.course_session.group

    @staticmethod
    def get_unit_count(obj):
        return obj.course_session.unit_count

    @staticmethod
    def get_exam_date(obj):
        exam_date_str = obj.course_session.final_exam_date
        if isinstance(exam_date_str, str):
            exam_date = parse_date(exam_date_str.replace('/', '-'))
        else:
            exam_date = exam_date_str

        exam_time_str = obj.course_session.final_exam_time
        if isinstance(exam_time_str, str):
            exam_time = parse_time(exam_time_str)
        else:
            exam_time = exam_time_str

        if exam_date and exam_time:
            formatted_date = exam_date.strftime('%Y-%m-%d')
            formatted_time = exam_time.strftime('%H:%M')
            exam_datetime = f'{formatted_date}T{formatted_time}'
            return exam_datetime
        return None


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'student_number', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            student_number=validated_data['student_number'],
            password=validated_data['password']
        )
        return user


class ScheduleSerializer(serializers.ModelSerializer):
    classes = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ['id', 'classes', 'status']

    def get_classes(self, obj):
        class_sessions = obj.classes.all()
        return ClassSessionAllDataSerializer(class_sessions, many=True, context=self.context).data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'student_number']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code']


class ProfessorSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='department.name')

    class Meta:
        model = Professor
        fields = ['id', 'full_name', 'department']

    @staticmethod
    def get_name(obj):
        return f"{obj.full_name}"

    @staticmethod
    def get_rate(obj):
        return {
            "teachQuality": obj.teaching_rate,
            "scoring": obj.exam_difficulty_rate,
            "morality": obj.communication_rate
        }


class LecturerSerializer(ProfessorSerializer):
    rate = serializers.SerializerMethodField()

    class Meta:
        model = Professor
        fields = (ProfessorSerializer.Meta.fields + ['number_of_votes', 'rate'])

    @staticmethod
    def get_rate(obj):
        return {
            "teachQuality": obj.teaching_rate,
            "scoring": obj.exam_difficulty_rate,
            "morality": obj.communication_rate
        }


class CommentSerializer(serializers.ModelSerializer):
    professor = serializers.PrimaryKeyRelatedField(queryset=Professor.objects.all())
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()

    class Meta:
        model = CommentOnProfessors
        fields = ['id', 'professor', 'text', 'likes', 'dislikes']

    @staticmethod
    def get_likes(obj):
        return obj.count_likes()

    @staticmethod
    def get_dislikes(obj):
        return obj.count_dislikes()
