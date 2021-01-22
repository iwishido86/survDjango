import logging
from datetime import timezone
from random import random, randint

from astropy.io.votable.converters import Int
from django.db.models import Q, Max, Count, Sum, Avg, F
from django.db.models.functions import Substr
from django.forms import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import render
from plotly.offline import plot
from plotly.graph_objs import Scatter
import FinanceDataReader as fdr
import pandas as pd
from django.utils import timezone

import datetime
from .forms import UserLoginForm, SurvForm
from .models import SurvM, QuestionM, AnsM, ResultHstoryL, ResultM, ResultCommentL

from .serializers import RegistrationUserSerializer

logger = logging.getLogger(__name__)

def dev_note_view(request):

    template_name = 'survDjango/dev_note.html'


    context = {
    }

    return render(request, template_name, context)
