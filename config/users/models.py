from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Expertise(models.Model):
    field = models.CharField(max_length=20)

    def __str__(self):
        return self.field

class Role(models.Model):
    role = models.CharField(max_length=20)

    def __str__(self):
        return self.role

class User(AbstractUser):
    expertise = models.ManyToManyField(Expertise)
    role = models.ManyToManyField(Role)
