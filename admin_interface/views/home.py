import sys
from datetime import timedelta
from random import randrange

from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render
from django.utils import timezone

from admin_interface.models import EmplacementChoice
from admin_interface.models.adoptions import Adoption
from admin_interface.models.animaux import Animal
from admin_interface.models.proprietaires import Proprietaire
from admin_interface.models.sejours import Sejour


@login_required
def index(request):
    # Pour la sidebar
    selected = "tableau_bord"

    # Dates
    today = timezone.now()
    interval = timezone.now() + timedelta(days=7)
    interval_str = interval.strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")
    # Partie pension
    arrivees_pension = (
        Sejour.objects.filter(date_arrivee__gt=today)
        .filter(date_arrivee__lt=interval)
        .count()
    )
    departs_pension = (
        Sejour.objects.filter(date_depart__gt=today)
        .filter(date_depart__lt=interval)
        .count()
    )
    presences = (
        Sejour.objects.filter(date_arrivee__lt=today)
        .filter(date_depart__gt=today)
        .count()
    )
    # Partie refuge
    rdv_veterinaire = (
        Animal.objects.filter(emplacement=EmplacementChoice.REFUGE.name)
        .filter(date_visite__gt=today)
        .filter(date_visite__lt=interval)
        .count()
    )
    recuperations = (
        Animal.objects.filter(emplacement=EmplacementChoice.REFUGE.name)
        .filter(date_arrivee__gt=today)
        .filter(date_arrivee__lt=interval)
        .count()
    )
    adoptions = (
        Adoption.objects.filter(date__gt=today).filter(date__lt=interval).count()
    )

    return render(request, "admin_interface/tableau_bord.html", locals())

@login_required
def stats(request):
    selected = "statistiques"

    labels = []
    data = []
    colors = []

    queryset = Proprietaire.objects.all()
    for proprietaire in queryset:
        labels.append(proprietaire.user.username)
        data.append(proprietaire.animal_set.all().count())
        print("Calcul couleurs \n")
        color = "rgb("+ str(randrange(0,255)) + "," + str(randrange(255)) + "," + str(randrange(255)) + ")"
        print(color)
        sys.stdout.flush()
        colors.append(color)
    return render(request, "admin_interface/statistiques.html", {
        'labels':labels,
        'data':data,
        'colors':colors,
        'selected':selected,
    })