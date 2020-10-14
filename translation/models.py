from django.db import models
from users.models import User
from django.urls import reverse


# Create your models here.
class Phase(models.Model):
    name = models.CharField(max_length=100)
    deadline = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=200)
    client = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dashboard')


class File(models.Model):
    name = models.CharField(max_length=200)
    workers = models.ManyToManyField(User)
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True)
    file = models.FileField(blank=True, null=True)
    phase = models.ManyToManyField(Phase)

    def __str__(self):
        return self.name
