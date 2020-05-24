import sys
from datetime import timedelta, datetime
import calendar
import locale

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
    # Adoptions pour l'année en cours
    data_adoption_current = []
    # Adoptions pour l'année précédente
    data_adoption_past = []
    

    adoptions = Adoption.objects.all()
    # Pour que les mois soient en français
    locale.setlocale(locale.LC_ALL, 'fr_FR')
    date = datetime.now()

    i = 1
    while (i < 13):
        labels_adoption.append("\n Mois " + calendar.month_name[i])
        data_adoption_current.append(adoptions.filter(date__year=date.year).filter(date__month=i).count())
        data_adoption_past.append(adoptions.filter(date__year=date.year-1).filter(date__month=i).count())
        i += 1

    pensions_calculees = Sejour.objects.filter(date_arrivee__year=date.year).\
                             values('proprietaire__user__last_name','proprietaire__user__first_name'). \
        annotate(total_pensions=Sum('nb_jours')).order_by('total_pensions')[:5]
    palmares = []

    for pension in pensions_calculees:
        palmares.insert(0,DotDict(pension))


    return render(request, "admin_interface/statistiques.html", {
        'labels_adoption':labels_adoption,
        'data_adoption_current':data_adoption_current,
        'data_adoption_past': data_adoption_past,
        'selected':selected,
        'current':date.year,
        'past': date.year-1,
        'palmares':palmares,
    })

class DotDict( dict):
    def __getattr__( self, attr):
        return self[attr] # or, return self.get( attr, default_value)