from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User, Organization
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    user_id = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if not data['first_name']:
            raise serializers.ValidationError({"first_name": "First name is required"})
        if not data['last_name']:
            raise serializers.ValidationError({"last_name": "Last name is required"})
        if not data['password']:
            raise serializers.ValidationError({"password": "Password is required"})
        return data
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_user_id(self, value):
        if User.objects.filter(user_id=value).exists():
            raise serializers.ValidationError("A user with this user ID already exists.")
        return value

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
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