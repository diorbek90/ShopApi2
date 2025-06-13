from rest_framework import serializers
# from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from .models import ConfirmationCode
from users.models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.timezone import now

class UserBaseSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField()


class AuthValidateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class RegisterValidateSerializer(UserBaseSerializer):
    def validate_username(self, username):
        try:
            CustomUser.objects.get(username=username)
        except:
            return username
        raise ValidationError('User уже существует!')

    def validate_email(self, email):
        try:
            CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return email
        raise ValidationError('Email уже используется!')

class ConfirmationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        code = attrs.get('code')

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError('User не существует!')

        try:
            confirmation_code = ConfirmationCode.objects.get(user=user)
        except ConfirmationCode.DoesNotExist:
            raise ValidationError('Код подтверждения не найден!')

        if confirmation_code.code != code:
            raise ValidationError('Неверный код подтверждения!')

        return attrs
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token
    

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['birth_date'] = str(user.birth_date)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if user.birth_date:
            today = now().date()
            age = today.year - user.birth_date.year - (
                (today.month, today.day) < (user.birth_date.month, user.birth_date.day)
            )
            if age < 18:
                raise serializers.ValidationError("You must be at least 18 years old.")

        return data