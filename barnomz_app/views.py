from django.contrib.auth import authenticate, login as django_login, logout as django_logout, logout, login
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password

from .edu import reset_edu_data
from .forms import RegisterForm, LoginForm
from .models import Schedule, ClassSession, Department, Course, Professor, CommentOnProfessors, CommentLike, User
from .serializers import UserSerializer, ScheduleSerializer, DepartmentSerializer, CourseSerializer, \
    ProfessorSerializer, CommentSerializer, RegisterSerializer
from rest_framework.authtoken.models import Token


# use this decorator to make sure that the user is authenticated before accessing the views that need users to login
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])

@api_view(['POST'])
def signup(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"message": "Successfully logged in.", "data": {"token": token.key}}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({"message": "Successfully logged out."})


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


@api_view(['POST'])
def like_comment(request, comment_id):
    try:
        comment = CommentOnProfessors.objects.get(id=comment_id)
        # Check if the user has already liked/disliked this comment
        existing_like = CommentLike.objects.filter(user=request.user, comment=comment).first()
        if existing_like:
            if existing_like.like:
                return Response({'message': 'You have already liked this comment.'}, status=status.HTTP_400_BAD_REQUEST)
            existing_like.like = True
            existing_like.save()
            return Response({'message': 'Your dislike has been changed to a like.'})
        else:
            CommentLike.objects.create(user=request.user, comment=comment, like=True)
            return Response({'message': 'You liked the comment.'})
    except CommentOnProfessors.DoesNotExist:
        return Response({'message': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def dislike_comment(request, comment_id):
    try:
        comment = CommentOnProfessors.objects.get(id=comment_id)
        existing_like = CommentLike.objects.filter(user=request.user, comment=comment).first()
        if existing_like:
            if not existing_like.like:
                return Response({'message': 'You have already liked this comment.'}, status=status.HTTP_400_BAD_REQUEST)
            existing_like.like = False
            existing_like.save()
            return Response({'message': 'Your dislike has been changed to a like.'})
        else:
            CommentLike.objects.create(user=request.user, comment=comment, like=True)
            return Response({'message': 'You disliked the comment.'})
    except CommentOnProfessors.DoesNotExist:
        return Response({'message': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def filling_data(request):
    try:
        reset_edu_data()
        print("salam")
        return Response({'message': 'SUCCESS.'})
    except:
        return Response({'message': 'Failed.'}, status=status.HTTP_404_NOT_FOUND)
