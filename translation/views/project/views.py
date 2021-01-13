from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, View, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import render

from ...models import Project, SentenceParser
from ...seg_creators import create_file_and_segments

from ...helpers import (
    all_forms_valid,
    is_all_supported,
    FILE_NOT_SUPPORTED_MSG,
)

from ...forms import (
    FileCreateForm,
    ProjectCreateForm,
    ProjectUpdateForm,
    SentenceParserForm,
)


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    context_object_name = "projects"


class ProjectCreateView(LoginRequiredMixin, View):
    model = Project
    form_classes = {
        "project": ProjectCreateForm,
        "files": FileCreateForm,
        "sentence_parser": SentenceParserForm,
    }
    success_url = reverse_lazy("dashboard")
    template_name = "translation/project_form.html"
    http_method_names = ["get", "post"]

    def get(self, request, *args, **kwargs):
        form = dict(self.form_classes)
        form["project"] = ProjectCreateForm(
                                        initial={'user': request.user}
                                        )
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = dict(self.form_classes)
        project_form = form["project"](request.POST)
        files_form = form["files"](request.POST, request.FILES)
        sentence_parser = form["sentence_parser"](request.POST)
        all_forms = [project_form, files_form, sentence_parser]

        if not all_forms_valid(all_forms):
            return redirect("project-create")

        project = project_form.save(commit=False)
        project.user = request.user
        fi_list = request.FILES.getlist("file_field")

        if not is_all_supported(fi_list):
            messages.error(request, FILE_NOT_SUPPORTED_MSG)
            return redirect("project-create")

        project_form.save()
        parser = sentence_parser.save(commit=False)
        parser.project = project
        sentence_parser.save()

        create_file_and_segments(parser, fi_list, project)

        return redirect(self.success_url)


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    success_url = reverse_lazy("dashboard")

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    model = Project
    form_classes = {
        "project": ProjectCreateForm,
        "files": FileCreateForm,
        "sentence_parser": SentenceParserForm,
    }
    success_url = reverse_lazy("dashboard")
    template_name = "translation/project_update_form.html"
    http_method_names = ["get", "post"]

    def get_object(self):
        pk = self.kwargs.get("pk")
        return self.model.objects.get(pk=pk)

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user

    def get(self, request, *args, **kwargs):
        project = self.get_object()
        sentence_parser = SentenceParser.objects.filter(project=project).last()
        form_classes = {
            "project": ProjectUpdateForm(instance=project),
            "files": FileCreateForm,
            "sentence_parser": SentenceParserForm(instance=sentence_parser),
        }

        form = form_classes
        fis = project.files.all()

        context = {"form": form, "files": fis}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        project = self.get_object()
        project_form = self.form_classes["project"](request.POST,
                                                    instance=project)
        files_form = self.form_classes["files"](request.POST, request.FILES)
        sentence_parser = self.form_classes["sentence_parser"](request.POST)

        all_forms = [project_form, files_form, sentence_parser]

        if not all_forms_valid(all_forms):
            return redirect("project-create")

        project = project_form.save(commit=False)
        project.user = request.user
        fi_list = request.FILES.getlist("file_field")
        project_form.save()

        if not is_all_supported(fi_list):
            messages.error(request, FILE_NOT_SUPPORTED_MSG)
            return redirect("project-create")

        parser = sentence_parser.save(commit=False)
        parser.project = project
        create_file_and_segments(parser, fi_list, project)
        sentence_parser.save()

        return redirect(self.success_url)


class ProjectDeleteAllView(LoginRequiredMixin, View):
    model = Project
    success_url = reverse_lazy("dashboard")
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        projects = Project.objects.filter(user=user)
        projects.delete()

        return redirect(self.success_url)
