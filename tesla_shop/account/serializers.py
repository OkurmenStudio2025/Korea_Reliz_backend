from rest_framework import serializers
from django.contrib.auth import get_user_model
from .tasks import send_activation_code
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class  Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'date_joined', 'is_active', 'role', 'country', 'id']


class RegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'password', 'password_confirm', 'country']  

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        country = validated_data.get('country')
        user = User(
            phone_number=validated_data['phone_number'],
            first_name=first_name,
            last_name=last_name,
            country=country
        )  
        user.set_password(password)
        user.save()

        verification, created = CustomUser.objects.get_or_create(
            phone_number=user.phone_number
        )
        if not created:
            verification.create_verification_code()  

        send_activation_code.delay(verification.verification_code, user.phone_number)  
        return user

class CustomTokenRefreshSerializers(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        return data
    
class CustomTokenObtainPairSerializers(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        print('role')
        print(f"User role: {user.role}")  

        token['role'] = user.role   

        return token
    
class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=50)

    def validate_phone_number(self, value):
        if not CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Пользователь с таким номером телефона не найден.")
        return value

class VerifyResetCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=50)
    verification_code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = CustomUser.objects.get(phone_number=data['phone_number'], verification_code=data['verification_code'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Неверный номер телефона или код.")
        
        if not user.is_code_valid():  
            raise serializers.ValidationError("Код подтверждения истек.")
        
        return data
    
class ResetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=50)
    verification_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Пароли не совпадают.")
        
        try:
            user = CustomUser.objects.get(phone_number=data['phone_number'], verification_code=data['verification_code'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Неверный номер телефона или код подтверждения.")
        
        if not user.is_code_valid():
            raise serializers.ValidationError("Код подтверждения истек.")
        
        return data