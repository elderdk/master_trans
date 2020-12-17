from pathlib import Path
import re
from shutil import copyfile
from zipfile import ZipFile

from django.db.models import Q

from ..file_generators import TargetGenerator
from ..models import Paragraph, Segment, Tag


class DocxGenerator(TargetGenerator):

    def __init__(self, pf):
        self.projectfile = pf
    
    