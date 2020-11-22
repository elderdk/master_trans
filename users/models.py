from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Expertise(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Role(models.Model):
    role = models.CharField(max_length=20)

    def __str__(self):
        return self.role


class User(AbstractUser):
    expertise = models.ManyToManyField(Expertise, related_name='users')
    role = models.ManyToManyField(Role)
    is_client = models.BooleanField(default=False, verbose_name='is_client')
