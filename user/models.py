from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

# Create your models here.

class User(AbstractUser):
    
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True )

    class Types(models.TextChoices):
        APPLICANT = "APPLICANT" ,"Applicant"
        RECRUITER  = "RECRUITER" , "Recruiter"

    base_type = Types.APPLICANT

    type = models.CharField(_("Type"), max_length=50, choices=Types.choices, default=base_type)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Applicant(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE, primary_key=True)
    profilePic = models.ImageField(upload_to='profilePic/', default='')
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    dob = models.DateField()
    gender = models.CharField(max_length=10 , blank=True , null=True)
    pob = models.CharField(max_length=100 , blank=True , null=True)           #place of birth
    nationality = models.CharField(max_length=100)   
    citizenship = models.CharField(max_length=100 , blank=True , null=True)
    cod = models.CharField(max_length=100 , blank=True , null=True)           #country of domicile
    maritalStat = models.CharField(max_length=100 , blank=True , null=True)   #marital status
    religion = models.CharField(max_length=100 , blank=True , null=True)
    address = models.TextField( blank=True , null=True)
    code = models.CharField(max_length=5)                    #home address
    phoneNo = models.CharField(max_length=100 , blank=True , null=True)
    icPass = models.CharField(max_length=20 , blank=True , null=True) #ic or passport number
    icColor = models.CharField(max_length=20, blank=True, null=True)
    submission = models.IntegerField(default=0)       
    # highQual = models.CharField(max_length=40 , blank=True, null=True)       #highest qualification the applicant have
    # yearsExp = models.IntegerField(blank=True , null=True) 
    
    def __str__(self):
        return self.user.email
    

"""

@receiver(post_save, sender=User)
def create_applicant(sender, instance, created, **kwargs):
    if created:
        Applicant.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.applicant.save()
"""
