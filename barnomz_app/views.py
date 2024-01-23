import requests
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.views import APIView

from .forms import RegisterForm
from .models import Schedule, ClassSession, Department, Course, Professor, CommentOnProfessors
from .serializers import UserSerializer, ScheduleSerializer, DepartmentSerializer, CourseSerializer, \
    ProfessorSerializer, CommentSerializer
from rest_framework.authtoken.models import Token


# use this decorator to make sure that the user is authenticated before accessing the views that need users to login
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])


@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.auth.delete()
    return Response(status=status.HTTP_200_OK)


class ScheduleList(APIView):
    def get(self, request, format=None):
        user_id = request.user.id
        schedules = Schedule.objects.filter(user=user_id)
        serializer = ScheduleSerializer(schedules, many=True)
        return Response({
            "status": "success",
            "message": "Schedules retrieved successfully.",
            "data": serializer.data
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_schedule(request):
    serializer = ScheduleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_schedule(request, schedule_id):
    try:
        schedule = Schedule.objects.get(pk=schedule_id, user=request.user)
        schedule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Schedule.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_course_to_schedule(request, schedule_id):
    try:
        schedule = Schedule.objects.get(pk=schedule_id, user=request.user)
        course_data = request.data
        course = ClassSession.objects.get(pk=course_data['id'])
        schedule.classes.add(course)
        schedule.save()
        all_schedules = Schedule.objects.filter(user=request.user)
        serializer = ScheduleSerializer(all_schedules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except (Schedule.DoesNotExist, ClassSession.DoesNotExist):
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_course_from_schedule(request, schedule_id):
    try:
        schedule = Schedule.objects.get(pk=schedule_id, user=request.user)
        course_data = request.data
        course = ClassSession.objects.get(pk=course_data['id'])
        schedule.classes.remove(course)
        schedule.save()
        all_schedules = Schedule.objects.filter(user=request.user)
        serializer = ScheduleSerializer(all_schedules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except (Schedule.DoesNotExist, ClassSession.DoesNotExist):
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def make_schedule_public(request, schedule_id):
    try:
        schedule = Schedule.objects.get(pk=schedule_id, user=request.user)
        schedule.status = "public"
        schedule.save()
        return Response(status=status.HTTP_200_OK)
    except Schedule.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def duplicate_schedule(request, schedule_id):
    schedule_to_duplicate = get_object_or_404(Schedule, pk=schedule_id, status="public")
    new_schedule = Schedule()
    new_schedule.user = request.user
    new_schedule.name = schedule_to_duplicate.name + " (Copy)"
    new_schedule.status = "private"
    new_schedule.is_default = False
    new_schedule.save()
    for class_session in schedule_to_duplicate.classes.all():
        new_schedule.classes.add(class_session)
    new_schedule.save()
    all_schedules = Schedule.objects.filter(user=request.user)
    serializer = ScheduleSerializer(all_schedules, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class GetAllDepartments(APIView):
    def get(self, request, format=None):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response({
            "status": "success",
            "message": "Departments retrieved successfully.",
            "data": serializer.data
        })


class GetCoursesOfDepartment(APIView):
    def get(self, request, department_id, format=None):
        courses = Course.objects.filter(department_id=department_id)
        serializer = CourseSerializer(courses, many=True)
        return Response({
            "status": "success",
            "message": "Courses retrieved successfully.",
            "data": serializer.data
        })


class GetLecturerInfo(APIView):
    def get(self, request, lecturer_id, format=None):
        lecturer = Professor.objects.get(pk=lecturer_id)
        serializer = ProfessorSerializer(lecturer)
        return Response({
            "status": "success",
            "message": "Lecturer info retrieved successfully.",
            "data": serializer.data
        })


# Todo: make this specific and fixed
class FilterPublicSchedules(APIView):
    def post(self, request, format=None):
        course_ids = request.data.get('filters', [])
        schedules = Schedule.objects.filter(status="public")
        for course_id in course_ids:
            schedules = schedules.filter(classes__course__id=course_id)
        serializer = ScheduleSerializer(schedules, many=True)
        return Response({
            "status": "success",
            "message": "Filtered schedules retrieved successfully.",
            "data": serializer.data
        })


class GetAllReviewsAboutLecturer(APIView):
    def get(self, request, lecturer_id, format=None):
        comments = CommentOnProfessors.objects.filter(professor_id=lecturer_id, is_deleted=False)
        serializer = CommentSerializer(comments, many=True)
        return Response({
            "status": "success",
            "message": "Reviews retrieved successfully.",
            "data": serializer.data
        })


class AddComment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveComment(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, comment_id, format=None):
        comment = get_object_or_404(CommentOnProfessors, pk=comment_id)
        comment.is_deleted = True
        comment.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
