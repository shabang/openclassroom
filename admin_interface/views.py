# -*- coding: utf-8 -*-
from decimal import Decimal
import sys

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.generic import CreateView, UpdateView

from _datetime import datetime, time, timedelta
from admin_interface.forms import (
    AdoptionForm,
    AdoptionFormNoProprietaire,
    AdoptionUpdateForm,
    AnimalCreateForm,
    AnimalSearchForm,
    AnimalUpdateForm,
    ConnexionForm,
    ProprietaireForm,
    ProprietaireSearchForm,
    SejourForm,
    SejourSearchForm,
    UserForm,
    VisiteSearchForm,
)
from admin_interface.models import (
    Adoption,
    Animal,
    EmplacementChoice,
    OuiNonChoice,
    ParametreTarifairePension,
    Proprietaire,
    Sejour,
    TarifAdoption,
    TarifJournalier,
    TypeSupplementChoice,
    VisiteMedicale,
)
