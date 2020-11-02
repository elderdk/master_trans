from django.contrib import admin
from .models import Project, ProjectFile, Phase, Segment, SentenceParser


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(ProjectFile)
class FileAdmin(admin.ModelAdmin):
    pass


@admin.register(Phase)
class PhaseAdmin(admin.ModelAdmin):
    pass


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    pass

@admin.register(SentenceParser)
class SentenceParserAdmin(admin.ModelAdmin):
    pass