from django.contrib import admin
from .models import Project, File, Phase

# Register your models here.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    pass

@admin.register(Phase)
class PhaseAdmin(admin.ModelAdmin):
    pass