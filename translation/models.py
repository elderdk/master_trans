from django.db import models
from users.models import User, Client
from django.urls import reverse


def get_file_path(instance, filename):
    return f"{instance.project.name}/{filename}"

class Phase(models.Model):
    name = models.CharField(max_length=100)
    deadline = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=200, verbose_name='Project Name')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True)
    client = models.ForeignKey(Client,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    deadline = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dashboard')


class File(models.Model):
    name = models.CharField(max_length=200, verbose_name='File(s)')
    workers = models.ManyToManyField(User, blank=True)
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True,
                                related_name='files')
    file = models.FileField(upload_to=get_file_path,
                            blank=True, 
                            null=True)

    def __str__(self):
        return self.name
