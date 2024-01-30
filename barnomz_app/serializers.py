from rest_framework import serializers

from barnomz_app.models import *


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'course_name', 'course_code', 'unit_count', 'presented_by', 'group',
                  'final_exam_date', 'final_exam_time', 'number_of_petitioners', 'number_of_capacity',
                  'number_of_enrolled', 'session', 'department', 'prerequisite_text', 'warning', 'grade', 'info']


class ClassSessionSerializer(serializers.ModelSerializer):
    course_details = CourseSerializer(source='course', read_only=True)

    class Meta:
        model = ClassSession
        fields = ['id', 'course_session', 'day_of_week', 'start_time', 'end_time', 'location']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'student_number', 'major', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            student_number=validated_data['student_number'],
            major=validated_data['major'],
            password=validated_data['password']
        )
        return user


class ScheduleSerializer(serializers.ModelSerializer):
    classes = ClassSessionSerializer(many=True, read_only=True)

    class Meta:
        model = Schedule
        fields = ['id', 'name', 'classes', 'status', 'is_default']


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
    name = serializers.SerializerMethodField()
    department = serializers.CharField(source='department.name')
    rate = serializers.SerializerMethodField()

    class Meta:
        model = Professor
        fields = ['id', 'full_name', 'college', 'number_of_votes', 'rate']

    @staticmethod
    def get_name(obj):
        return f"Dr. {obj.full_name}"

    @staticmethod
    def get_rate(obj):
        return {
            "teachQuality": obj.teaching_rate,
            "scoring": obj.exam_difficulty_rate,
            "morality": obj.communication_rate
        }


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentOnProfessors
        exclude = ['is_deleted', 'text', 'professor', 'date', 'is_anonymous']
