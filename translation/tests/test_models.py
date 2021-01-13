from django.test import TestCase
from ..models import Project, ProjectFile, SentenceParser, Segment
from users.models import User
from pathlib import Path
from translation.handlers.parse_docx import DocxSegmentCreator
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.


class ProjectFileTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create(
            username='tester',
            password='my_password',
            email='my_email@gmail.com'
        )

        cls.project = Project.objects.create(
            name='testProject',
            user=cls.user,

        )

        cls.parser = SentenceParser.objects.create(
            project=cls.project
        )

    def test_project_model(self):
        self.assertEqual(self.project.name, 'testProject')

    def test_parser_model(self):
        self.assertEqual(self.parser.project, self.project)
