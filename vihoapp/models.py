from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser

# Create your models here.
class User(AbstractBaseUser):
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    phone = models.CharField(max_length=10,blank=True)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=50,blank=True)
    industry = models.CharField(max_length=50,blank=True)
    vat_tax_id = models.CharField(max_length=50,null=True)
    last_login = models.DateTimeField(blank=True,null=True)
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.fname

class project(models.Model):
    name = models.CharField(max_length=200)
    client_name = models.CharField(max_length=200)
    rate = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    priority = models.CharField(max_length=200)
    size = models.CharField(max_length=200)
    start_date = models.DateField(blank=True,null=True)
    end_date = models.DateField(blank=True,null=True)
    details = models.CharField(max_length=200)
    user_id = models.ForeignKey(User, default=1, verbose_name="id", on_delete=models.SET_DEFAULT)


class Task(models.Model):
    title = models.CharField(max_length=200)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# import datafile models
class Datafile(models.Model):
    name = models.CharField(max_length=250)
    size = models.CharField(max_length=250,default=0)
    datacount = models.CharField(max_length=250,default=0)
    contentType = models.CharField(max_length=250,null=True)
    contentTypeExtra = models.CharField(max_length=250,null=True)
    charset = models.CharField(max_length=250,null=True)
    #data = models.TextField
    data = models.TextField(blank=True, null=True)
    columnData = models.TextField(blank=True, null=True)
    original_name = models.CharField(max_length=250)
    created = models.DateTimeField(default=timezone.now())
    modified = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey(User, default=1, verbose_name="id", on_delete=models.SET_DEFAULT)
    project_id = models.ForeignKey(project, default=1, verbose_name="id", on_delete=models.SET_DEFAULT)
    def __str__(self):
        return self.name