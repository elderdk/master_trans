import re

from django.db import models
from users.models import User, Client
from django.urls import reverse
from datetime import date


def get_file_path(instance, filename):
    project = instance.project
    parent_folder = 'project_files'
    client = project.client.name
    today = date.strftime(date.today(), '%Y%m')
    project_name = project.name
    filename = filename
    return f"{parent_folder}/{client}/{today}/{project_name}/{filename}"


class Phase(models.Model):
    name = models.CharField(max_length=100)
    deadline = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=200,
                            blank=False,
                            verbose_name='Project Name')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             )
    client = models.ForeignKey(Client,
                               on_delete=models.SET_NULL,
                               null=True,
                               blank=False,
                               related_name='client')
    deadline = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dashboard')


class ProjectFile(models.Model):
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


class Segment(models.Model):

    seg_id = models.IntegerField()
    file = models.ForeignKey(
        ProjectFile,
        on_delete=models.CASCADE,
        related_name='segments'
        )
    source = models.TextField()
    target = models.TextField(blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    NOT_TRANSLATED = 'NT'
    DRAFT = 'DR'
    TRANSLATED = 'TR'
    TRANSLATION_REJECTED = 'TJ'
    REVIWED = 'RV'
    REVIEW_REJECTED = 'RJ'
    SIGNED_OFF = 'SO'
    SIGN_OFF_REJECTED = 'SJ'

    SEGMENT_STATUSES = [
        (NOT_TRANSLATED, 'Not Translated'),
        (DRAFT, 'Draft'),
        (TRANSLATED, 'Translated'),
        (TRANSLATION_REJECTED, 'Translation Rejected'),
        (REVIWED, 'Reviewed'),
        (REVIEW_REJECTED, 'Review Rejected'),
        (SIGNED_OFF, 'Signed Off'),
        (SIGN_OFF_REJECTED, 'Sign-off Rejected')
    ]

    status = models.CharField(max_length=2,
                              choices=SEGMENT_STATUSES,
                              default=NOT_TRANSLATED
                              )

    def __str__(self):
        return self.source


class SentenceParser(models.Model):
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                related_name='sentence_parser')
    default_regex = models.CharField(max_length=255,
                                     default="(?<=[\"\'\.])(?<![s])\s+")
    exclusion = models.CharField(max_length=255,
                                 default="(?<!Mr\.)(?<!Mrs\.)(?<![^\.\,]\")")
    
    def create_segments(self, fi):
        with fi.file.open(mode='r') as f:
            regex = re.compile(self.full_regex, flags=re.UNICODE)
            sentences = regex.split(f.read())

            num = 1
            for sentence in sentences:
                Segment.objects.create(
                    file=fi,
                    source=sentence,
                    seg_id=num
                )
                num += 1

    @property
    def full_regex(self):
        return self.exclusion + self.default_regex
