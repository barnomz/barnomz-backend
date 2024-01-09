from rest_framework import serializers

from barnomz_app.models import *


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'course_name', 'course_code', 'unit_count', 'offered_by', 'group', 'day_of_week', 'start_time',
                  'end_time', 'final_exam_date', 'number_of_petitioners', 'number_of_capacity',
                  'number_of_enrolled', 'professor', 'session', 'department', 'prerequisite']


class ClassSessionSerializer(serializers.ModelSerializer):
    course_details = CourseSerializer(source='course', read_only=True)

    class Meta:
        model = ClassSession
        fields = ['id', 'course_details', 'day_of_week', 'start_time', 'end_time']


class ScheduleSerializer(serializers.ModelSerializer):
    classes = ClassSessionSerializer(many=True, read_only=True)

    class Meta:
        model = Schedule
        fields = ['id', 'name', 'classes', 'status', 'is_default']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']


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
        exclude = ['is_deleted']
