from django.contrib.auth import authenticate
from rest_framework import status, mixins, viewsets, exceptions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import MyUser
from account.seriazlizers import RegisterSerializer, UserSerializer, UserUpdateSerializer, LoginSerializer


class RegisterView(APIView):

    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('Вы успешно зарегистрировались!', status=status.HTTP_201_CREATED)


class LoginView(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
        if not user:
            raise exceptions.AuthenticationFailed('Username or password are incorrect')

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'last_name': user.last_name,
            'first_name': user.first_name,
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        user = request.user
        Token.objects.filter(user=user).delete()
        return Response('успешно вышли из системы', status=status.HTTP_200_OK)


class UserViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'email'
    lookup_url_kwarg = 'email'
    lookup_value_regex = '[\w@.]+'

    def get_permissions(self):
        if self.action in ['retrieve', 'partial_update', 'destroy', 'update']:
            permissions = [IsAuthenticated, ]
        else:
            permissions = [IsAuthenticated]
        return [permission() for permission in permissions]

    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}


class UserMe(APIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = UserSerializer

    def get(self, request, format=None):
        return Response(self.serializer_class(request.user, context={"request": request}).data)

    def patch(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = UserUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serialized = UserSerializer(data=request.data)
        if serialized.is_valid():
            serialized.save()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        return Response(self.serializer_class(request.user, context={"request": request}).data)