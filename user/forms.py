from django import forms
from .models import Applicant
 
 
class ProfileForm(forms.ModelForm):
 
    class Meta:
        model = Applicant
        fields =['profilePic']