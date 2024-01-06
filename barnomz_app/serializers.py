from rest_framework import serializers

from barnomz_app.models import User, Course
from .models import Schedule, ClassSession


class CourseSerializer(serializers.ModelSerializer):
    offered_by_name = serializers.CharField(source='offered_by.last_name')
    location_name = serializers.CharField(source='location.class_name')

    class Meta:
        model = Course
        fields = ['id', 'course_name', 'course_code', 'unit_count', 'offered_by_name', 'group', 'day_of_week',
                  'start_time', 'end_time', 'location_name', 'final_exam_date', 'number_of_petitioners',
                  'number_of_capacity', 'number_of_enrolled']


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
