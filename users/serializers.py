from .models import User
from django.contrib import auth
from rest_framework import serializers
from django.contrib.auth.models import Group
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phonenumber']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')
        if not username.isalnum():
            raise serializers.ValidationError(
                self.default_error_messages)
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(max_length=255, min_length=3)
    tokens = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['password', 'username', 'tokens']


    def get_tokens(self, obj):
        user = User.objects.get(username=obj['username'])
        print(user)
        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    # def get_tokens(self, obj):
    #     try:
    #         if isinstance(obj, dict):
    #             # If obj is a dictionary from validate
    #             username = obj.get('username')
    #             user = User.objects.get(username=username)
    #             return {
    #                 'refresh': user.tokens()['refresh'],
    #                 'access': user.tokens()['access']
    #             }
    #         else:
    #             # If obj is already a User instance
    #             return {
    #                 'refresh': obj.tokens()['refresh'],
    #                 'access': obj.tokens()['access']
    #             }
    #     except Exception as e:
    #         print(f"Error in get_tokens: {str(e)}")
    #         return {}


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')
