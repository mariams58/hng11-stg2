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

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['org_id', 'name', 'description', 'users']

