from rest_framework import serializers

from barnomz_app.models import *


class CourseSerializer(serializers.ModelSerializer):
    presented_by = serializers.CharField(max_length=255)

    class Meta:
        model = Course
        fields = ['id', 'course_name', 'course_code', 'unit_count', 'presented_by', 'group',
                  'final_exam_date', 'final_exam_time', 'number_of_petitioners', 'number_of_capacity',
                  'number_of_enrolled', 'location', 'department', 'warning', 'grade', 'info']

    def get_presented_by(self):
        return Professor.objects.get(self.presented_by).full_name


class ClassSessionSerializer(serializers.ModelSerializer):
    day_of_week = serializers.SerializerMethodField()

    class Meta:
        model = ClassSession
        fields = ['id', 'day_of_week', 'start_time', 'end_time', 'location']

    def get_day_of_week(self, obj):
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
        return day_to_int.get(day_name, None)


class ClassSessionAllDataSerializer(ClassSessionSerializer):
    course_name = serializers.SerializerMethodField()
    course_code = serializers.SerializerMethodField()
    presented_by = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()

    class Meta(ClassSessionSerializer.Meta):
        fields = ClassSessionSerializer.Meta.fields + ['course_name', 'course_code', 'presented_by', 'group']

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

    class Meta:
        model = CommentOnProfessors
        fields = '__all__'
