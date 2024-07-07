# from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Organization
from .serializers import UserSerializer, OrganizationSerializer
import jwt, uuid

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        data['user_id'] = str(uuid.uuid4())  # Generate unique user_id
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create a default organization for the user
            org_id = str(uuid.uuid4())
            organization = Organization.objects.create(
                org_id=org_id,
                name=f"{user.first_name}'s Organisation",
                description=f"Default organization for {user.first_name}"
            )
            # Generate a JWT token
            token = jwt.encode({'user_id': user.id}, 'your_secret_key', algorithm='HS256')
            return Response({
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": token,
                    "user": serializer.data
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "statusCode": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            token = RefreshToken.for_user(user)
            response_data = {
                "status": "success",
                "message": "Login successful",
                "data": {
                    "accessToken": str(token.access_token),
                    "user": UserSerializer(user).data
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({"status": "Bad request", "message": "Authentication failed", "statusCode": 401}, status=status.HTTP_401_UNAUTHORIZED)

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserOrganizationsView(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.organizations.all()

class OrganizationDetailView(generics.RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.organizations.all()

class OrganizationCreateView(generics.CreateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org = serializer.save()
        org.users.add(request.user)
        org.save()
        response_data = {
            "status": "success",
            "message": "Organisation created successfully",
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
