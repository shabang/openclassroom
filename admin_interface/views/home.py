import sys
from datetime import timedelta

from django.db.models import Sum

from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render
from django.utils import timezone

from admin_interface.models import EmplacementChoice
from admin_interface.models.adoptions import Adoption
from admin_interface.models.animaux import Animal
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

    labels_adoption = []
    data_adoption = []
    labels_pension = []
    data_pension = []
    

    adoptions = Adoption.objects.all()
    i = 0
    while (i < 52):
        labels_adoption.append("\n Semaine " + str(i))
        labels_pension.append("\n Semaine " + str(i))
        data_adoption.append(adoptions.filter(date__year=2020).filter(date__week=i).count())
        added_data = Sejour.objects.filter(date_arrivee__year=2020).filter(date_arrivee__week=i).\
            aggregate(Sum('nb_jours'))['nb_jours__sum']
        if added_data:
            data_pension.append(added_data)
        else:
            data_pension.append(0)
        i += 1

    return render(request, "admin_interface/statistiques.html", {
        'labels_adoption':labels_adoption,
        'data_adoption':data_adoption,
        'labels_pension': labels_pension,
        'data_pension': data_pension,
        'selected':selected,
    })