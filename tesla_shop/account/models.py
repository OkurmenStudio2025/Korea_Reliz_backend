from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.crypto import get_random_string

class CustomUserManager(BaseUserManager):
    def _create_user(self, phone_number, password, **extra):
        if not phone_number:
            raise ValueError('Phone - поле обязательное')
        first_name = extra.get('first_name')
        last_name = extra.get('last_name')
        role = extra.get('role')
        user = self.model(phone_number=phone_number, first_name=first_name, last_name=last_name, role=role, **extra)
        user.set_password(password)
        user.save()
        return user


    def create_user(self, phone_number, password, **extra):
        user = self._create_user(phone_number, password, **extra)
        user.create_verification_code()
        user.save()
        return user

    def create_superuser(self, phone_number, password, **extra):
        user = self.create_user(phone_number, password, **extra)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True  
        user.save()
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    country = models.CharField(max_length=10, verbose_name='страна', null=True, blank=True)
    role = models.CharField(max_length=50, null=True, blank=True) 
    first_name = models.CharField(max_length=30, verbose_name='имя', null=True, blank=True)
    last_name = models.CharField(max_length=30, verbose_name='фамилия', blank=True, null=True)
    phone_number = models.CharField(max_length=50, unique=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)  
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False) 
    expires_at = models.DateTimeField(null=True, blank=True)


    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    
    def create_verification_code(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = get_random_string(length=6, allowed_chars='0123456789')
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)  
        super().save(*args, **kwargs)

    def is_code_valid(self):
        return timezone.now() < self.expires_at

    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"{self.phone_number} - {self.verification_code}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
