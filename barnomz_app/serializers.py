from rest_framework import serializers

from barnomz_app.models import *


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'course_name', 'course_code', 'unit_count', 'presented_by', 'group',
                  'final_exam_date', 'final_exam_time', 'number_of_petitioners', 'number_of_capacity',
                  'number_of_enrolled', 'location', 'department', 'warning', 'grade', 'info']


class ClassSessionSerializer(serializers.ModelSerializer):
    course_details = CourseSerializer(source='course', read_only=True)

    class Meta:
        model = ClassSession
        fields = ['id', 'course_session', 'day_of_week', 'start_time', 'end_time', 'location']


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
    classes = serializers.PrimaryKeyRelatedField(queryset=ClassSession.objects.all(), many=True, required=False)

    class Meta:
        model = Schedule
        fields = ['id', 'classes', 'status']


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
    class Meta:
        model = CommentOnProfessors
        exclude = ['is_deleted', 'text', 'professor', 'date', 'is_anonymous']
