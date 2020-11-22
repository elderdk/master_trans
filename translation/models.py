import re
import uuid

from django.db import models
from users.models import User
from django.urls import reverse
from datetime import date


DEFAULT_REGEX = r"(?<=[\"'.])(?<![s])\s+"
REGEX_EXCLUSION = r'(?<!Mr.)(?<!Mrs.)(?<![^.,]")'


def get_file_path(instance, filename):
    project = instance.project
    parent_folder = 'project_files'
    user = project.user.username
    today = date.strftime(date.today(), '%Y%m')
    project_name = project.name
    filename = filename
    return f"{parent_folder}/{user}/{today}/{project_name}/source/{filename}"


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
                             related_name='user'
                             )
    
    deadline = models.DateTimeField(blank=True, null=True)

    translators = models.ManyToManyField(User, related_name='translators')
    reviewers = models.ManyToManyField(User, related_name='reviewers')
    soers = models.ManyToManyField(User, related_name='soers')

    translation_id = models.UUIDField(default=uuid.uuid4, editable=False)
    review_id = models.UUIDField(default=uuid.uuid4, editable=False)
    sign_off_id = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dashboard')

    @property
    def workers(self):
        querysets = [
            self.translators.all(),
            self.reviewers.all(),
            self.soers.all()
            ]
        return [user for queryset in querysets for user in queryset]


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
    REVIEWED = 'RV'
    REVIEW_REJECTED = 'RJ'
    SIGNED_OFF = 'SO'
    SIGN_OFF_REJECTED = 'SJ'

    SEGMENT_STATUSES = [
        (NOT_TRANSLATED, 'Not Translated'),
        (DRAFT, 'Draft'),
        (TRANSLATED, 'Translated'),
        (TRANSLATION_REJECTED, 'Translation Rejected'),
        (REVIEWED, 'Reviewed'),
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
                                     default=DEFAULT_REGEX)
    exclusion = models.CharField(max_length=255,
                                 default=REGEX_EXCLUSION)

    def create_segments(self, fi):
        with fi.file.open(mode='r') as f:
            regex = re.compile(self.full_regex, flags=re.UNICODE)
            sentences = regex.split(f.read())

            for num, sentence in enumerate(sentences, start=1):
                Segment.objects.create(
                    file=fi,
                    source=sentence,
                    seg_id=num
                )

    @property
    def full_regex(self):
        return self.exclusion + self.default_regex


class ShortDistanceSegment(models.Model):
    segment = models.ForeignKey(Segment,
                                on_delete=models.CASCADE,
                                related_name='short_distance_seg'
                                )
    distance = models.FloatField()
    html_snippet = models.TextField()
