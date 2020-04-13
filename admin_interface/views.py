# -*- coding: utf-8 -*-
import sys
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView
from admin_interface.forms import AnimalSearchForm, ProprietaireSearchForm, AnimalUpdateForm, \
    AnimalCreateForm, ConnexionForm, VisiteSearchForm, SejourSearchForm, UserForm, ProprietaireForm, SejourForm, \
    AdoptionFormNoProprietaire, AdoptionForm, AdoptionUpdateForm
from admin_interface.models import Animal, Proprietaire, VisiteMedicale, Sejour, \
    Adoption, TarifJournalier, TarifAdoption, ParametreTarifairePension, \
    TypeSupplementChoice, OuiNonChoice, EmplacementChoice
from django.urls import reverse_lazy
from _datetime import timedelta, datetime, time
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.shortcuts import redirect
from django.utils.dateparse import parse_date
from django.core.exceptions import ObjectDoesNotExist




















