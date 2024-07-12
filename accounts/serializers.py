from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User, Organisation
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=make_password(validated_data['password']),
            phone=validated_data.get('phone')
        )
        return user
    
    def validate(self, data):
        errors = []
        if not data['first_name']:
            errors.append({"field": "first_name", "message": "First name is required"})
        if not data['last_name']:
            errors.append({"field": "last_name", "message": "Last name is required"})
        if not data['password']:
            errors.append({"field": "password", "message": "Password is required"})
        if errors:
            raise serializers.ValidationError({"errors": errors})
        return data

class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['org_id', 'name', 'description', 'users']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid email or password")

            if not user.check_password(password):
                raise serializers.ValidationError("Invalid email or password")

            data['user'] = user
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'")
        return data
    
class AddUserToOrganizationSerializer(serializers.Serializer):
    user_id = serializers.CharField()

class AddUserToOrganizationSerializer(serializers.Serializer):
    user_id = serializers.CharField()