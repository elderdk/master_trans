from django.contrib import admin
from .models import Paragraph, Project, ProjectFile, Phase, Segment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(ProjectFile)
class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'project')


@admin.register(Phase)
class PhaseAdmin(admin.ModelAdmin):
    pass


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    pass


@admin.register(Paragraph)
class ParagraphAdmin(admin.ModelAdmin):
    pass
