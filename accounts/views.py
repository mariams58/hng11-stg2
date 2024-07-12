# from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Organisation
from .serializers import UserSerializer, OrganisationSerializer, LoginSerializer, AddUserToOrganizationSerializer
from django.conf import settings
from django.contrib.auth.hashers import make_password
import jwt, uuid

# Utility function to get current user from token
def get_current_user(request):
    token = request.headers.get('Authorization').split()[1]
    decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    return User.objects.get(id=decoded_data['user_id'])

class RegisterView(APIView):
     def post(self, request):
        data = request.data
        #data['user_id'] = str(uuid.uuid4())  # Generate unique user_id
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create a default organization for the user 
            #org_id = str(uuid.uuid4())
            org_name = f"{user.first_name}'s Organisation"
            organisation = Organisation.objects.create(
                 name=org_name,
                 description=f"Default organization for {user.first_name}"
             )
            organisation.users.add(user)
            organisation.save()
             # Generate a JWT token 
            refresh = RefreshToken.for_user(user)
            return Response({
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken":str(refresh.access_token) ,
                    "user": serializer.data
                }
                }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = jwt.encode({'user_id': user.id}, settings.SECRET_KEY, algorithm='HS256')
            response_data = {
                "status": "success",
                "message": "Login successful",
                "data": {
                    "accessToken": refresh,
                    "data": {
                        "user_id": user.user_id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "phone": user.phone,
                    }
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({"status": "Bad request", "message": "Authentication failed", "statusCode": 401}, status=status.HTTP_401_UNAUTHORIZED)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_current_user(request)
        if user.user_id == user_id:
            serializer = UserSerializer(user)
            return Response({
                "status": "success",
                "message": "User details fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "Bad request",
            "message": "You can only access your own details"
        }, status=status.HTTP_400_BAD_REQUEST)

class ListOrganizationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = get_current_user(request)
        organizations = user.organizations.all() | user.created_organizations.all()
        serializer = OrganisationSerializer(organizations, many=True)
        return Response({
            "status": "success",
            "message": "Organizations fetched successfully",
            "data": {"organizations": serializer.data}
        }, status=status.HTTP_200_OK)

class UserOrganizationsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.organizations.all()

class OrganizationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, org_id):
        user = get_current_user(request)
        try:
            organization = Organisation.objects.get(org_id=org_id)
        except Organisation.DoesNotExist:
            return Response({
                "status": "Not found",
                "message": "Organization not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user in organization.users.all() or user == organization.created_by:
            serializer = OrganisationSerializer(organization)
            return Response({
                "status": "success",
                "message": "Organization details fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "Bad request",
            "message": "You do not have access to this organization"
        }, status=status.HTTP_400_BAD_REQUEST)
    
class OrganizationCreateView(APIView):
    serializer_class = OrganisationSerializer
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

class AddUserToOrganizationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, org_id):
        user = get_current_user(request)
        serializer = AddUserToOrganizationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                organization = Organisation.objects.get(org_id=org_id)
            except Organisation.DoesNotExist:
                return Response({
                    "status": "Not found",
                    "message": "Organization not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            if user == organization.created_by:
                try:
                    user_to_add = User.objects.get(user_id=serializer.data['user_id'])
                except User.DoesNotExist:
                    return Response({
                        "status": "Not found",
                        "message": "User not found"
                    }, status=status.HTTP_404_NOT_FOUND)
                
                organization.users.add(user_to_add)
                return Response({
                    "status": "success",
                    "message": "User added to organization successfully",
                }, status=status.HTTP_200_OK)
            return Response({
                "status": "Bad request",
                "message": "Only the organization creator can add users"
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "status": "Bad request",
            "message": "Client error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)