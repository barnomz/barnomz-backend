import requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.views import APIView

from .models import Schedule
from .serializers import UserSerializer, ScheduleSerializer
from rest_framework.authtoken.models import Token


# use this decorator to make sure that the user is authenticated before accessing the views that need users to login
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])


@api_view(['POST'])
def register(request):
    captcha_response = request.data.get('captcha_response')
    secret_key = 'your_recaptcha_secret_key'
    data = {
        'secret': secret_key,
        'response': captcha_response
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = r.json()
    if not result.get('success'):
        return Response({'captcha': 'Invalid Captcha'}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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