from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser, PermissionsMixin
from . managers import UserManager
# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=11, unique=True)
    full_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default= True)
    is_admin = models.BooleanField(default= False)
    
    objects = UserManager()




    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'full_name']


    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return True
        
    def has_module_perms(self, app_label):
        return True
    
    @property
    def is_staff(self):
        return self.is_admin
    


#this model is for otp code to get a code from sms from client phone number
class OtpCode(models.Model):
    phone_number = models.CharField(max_length=11)
    code = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now= True)

    def __str__(self):
        return f'{self.phone_number} - {self.code} - {self.created}'
    

    