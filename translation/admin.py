from django.contrib import admin
from .models import Project, ProjectFile, Phase


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(ProjectFile)
class FileAdmin(admin.ModelAdmin):
    pass


@admin.register(Phase)
class PhaseAdmin(admin.ModelAdmin):
    pass