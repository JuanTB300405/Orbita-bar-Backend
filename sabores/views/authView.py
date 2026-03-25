from ..serializers.UsuariosSerializer import UserSerializer 
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import action

from rest_framework import viewsets

class UserView(viewsets.ModelViewSet):
    
    serializer_class = UserSerializer

    @action(detail=False, methods=['POST'])
    def login(self, request):
        try:
            request.data["nombre"] = "admin"
            user = get_object_or_404(User, username=request.data["nombre"])

            if not user.check_password(request.data["contrasena"]):
                return Response({"error: " "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
            
            token, created = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(instance=user)

            return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_200_OK);
        except Exception as e:
            return Response({"Error": e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR);



    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        try:
            token = Token.objects.get(user_id=request.user.id)
            print(token)
            token.delete()
            return Response({"detail": "Sesión cerrada correctamente"}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"detail": "Token no encontrado"}, status=status.HTTP_400_BAD_REQUEST)
