from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest.http_statuses import HTTP_DOES_NOT_EXIST, HTTP_OK
from rest.rest_helper import get_validated_serializer, get_user_from_validated_data
from rest.serializers import IdSerializer, UserSerializer, UserHashSerializer
from session.models import Session
from suser.constants import PHONE_VALIDATORS
from suser.models import User


class UserLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=PHONE_VALIDATORS, help_text='9123456789')
    password = serializers.CharField(max_length=20)

class UserRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ("is_superuser", "is_staff", "is_active", "user_permissions", "groups")

class OnlyIdSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class UsersGetSerializer(serializers.Serializer):
    pass




@api_view(['POST'])
def user_get(request):
    """
    ---
    response_serializer: UserSerializer
    request_serializer: OnlyIdSerializer
    responseMessages:
        - code: HTTP_DOES_NOT_EXIST
          message: User doesn't exist
    """
    sdata = get_validated_serializer(request=request, serializer=OnlyIdSerializer).validated_data
    try:
        user = User.objects.get(id=sdata['id'])
    except Exception:
        return Response("No user with such id", status=HTTP_DOES_NOT_EXIST)
    return Response(UserSerializer(user).data, status=HTTP_OK)

@api_view(['POST'])
def users_get(request):
    """
    ---
    response_serializer: UserSerializer
    request_serializer: UsersGetSerializer
    """
    sdata = get_validated_serializer(request=request, serializer=UsersGetSerializer).validated_data
    users = User.objects.all()
    return Response(UserSerializer(users, many=True).data, status=HTTP_OK)


@api_view(['POST'])
def login(request):
    """
    ---
    response_serializer: IdSerializer
    request_serializer: UserLoginSerializer
    responseMessages:
        - code: HTTP_DOES_NOT_EXIST
          message: User doesn't exist
    """
    sdata = get_validated_serializer(request=request, serializer=UserLoginSerializer).validated_data
    user = User.objects.filter(phone=sdata['phone']).first()
    if ( user is None or not user.check_password(sdata['password'])):
        return Response("No user with such user", status=HTTP_DOES_NOT_EXIST)
    session = Session.get_for_user(user)
    return Response( IdSerializer({"hash": session.hash, 'id':user.pk}).data , status=HTTP_OK)


@api_view(['POST'])
def register(request):
    """
    ---
    response_serializer: IdSerializer
    request_serializer: UserRegisterSerializer
    """
    sdata = get_validated_serializer(request=request, serializer=UserRegisterSerializer).validated_data
    password = sdata['password']
    del sdata['password']
    user = User(**sdata)
    user.set_password(password)
    user.save()
    session = Session.get_for_user(user)
    return Response( IdSerializer({"hash": session.hash, 'id':user.pk}).data , status=HTTP_OK)
