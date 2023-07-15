from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


from .models import *

class TaskForm(forms.ModelForm):
    title = forms.CharField(max_length=200, widget= forms.Textarea(attrs={'placeholder':'Enter new task here. . .'}))
    class Meta:
        model = Task
        fields = '__all__' 

class CreateUserForm(UserCreationForm):
    fname = forms.CharField(max_length=200, label = "First Name")
    lname = forms.CharField(max_length=200, label = "Last Name")

    class Meta:
        model = User
        fields  = ['fname','lname', 'phone','email','company','industry','industry', 'vat_tax_id', 'password2']

class CreateLoginForm(AuthenticationForm):
    #email = forms.CharField(max_length=200, label = "Email")
    username = forms.CharField(label='Email')
    class Meta:
        model = User 

class UploadFileForm(forms.Form):
    type = forms.CharField(max_length=50)
    file = forms.FileField()
    