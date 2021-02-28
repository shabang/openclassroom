import sys
from datetime import timedelta, datetime
from decimal import Decimal

import calendar
import locale

from django.db.models import Sum, Q, Count, F

from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from admin_interface.forms.sejours import SejourStatsForm
from admin_interface.models import EmplacementChoice, OuiNonChoice
from admin_interface.models.adoptions import Adoption
from admin_interface.models.animaux import Animal
from admin_interface.models.sejours import Sejour


@login_required
def index(request):
    # Pour la sidebar
    selected = "tableau_bord"

    # Dates
    today = timezone.now().date()
    interval = timezone.now().date() + timedelta(days=7)
    interval_str = interval.strftime("%Y-%m-%d")
    interval_month = timezone.now().date() + timedelta(days=30)
    interval_month_str = interval_month.strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")
    day_interval = timezone.now().date() + timedelta(days=1)
    day_interval_str = day_interval.strftime("%Y-%m-%d")
    # Partie pension
    arrivees_pension = (
        Sejour.objects.filter(date_arrivee__gte=today)
        .filter(date_arrivee__lte=interval)
        .filter(annule=False)
        .count()
    )
    departs_pension = (
        Sejour.objects.filter(date_depart__gte=today)
        .filter(date_depart__lte=interval)
        .filter(annule=False)
        .count()
    )
    arrivees_pension_jour = (
        Sejour.objects.filter(date_arrivee__gte=today)
            .filter(date_arrivee__lte=day_interval)
            .filter(annule=False)
            .count()
    )
    departs_pension_jour = (
        Sejour.objects.filter(date_depart__gte=today)
            .filter(date_depart__lte=day_interval)
            .filter(annule=False)
            .count()
    )
    presences = (
        Sejour.objects.filter(date_arrivee__lte=day_interval)
        .filter(date_depart__gte=today)
        .filter(annule=False)
        .annotate(num_animaux=Count('animaux')) \
        .aggregate(Sum('num_animaux')).get("num_animaux__sum")
    )
    # Partie refuge
    rdv_veterinaire = (
        Animal.objects.filter(emplacement=EmplacementChoice.REFUGE.name)
        .filter(date_visite__gte=today)
        .filter(date_visite__lte=interval)
        .count()
    )
    recuperations = (
        Animal.objects.filter(emplacement=EmplacementChoice.REFUGE.name)
        .filter(date_arrivee__gte=today)
        .filter(date_arrivee__lte=interval)
        .count()
    )
    adoptions = (
        Adoption.objects.filter(date__gte=today).filter(date__lte=interval).count()
    )
    #Partie indicateurs paiements
    paiements_adoptions = Adoption.objects.filter(montant_restant__gt=Decimal('0'))
    nb_paiements_adoptions = paiements_adoptions.count()
    total_paiements_adoptions = paiements_adoptions.aggregate(Sum('montant_restant'))
    paiements_sejours = Sejour.objects.filter(annule=False).filter(montant_restant__gt=Decimal('0'))
    nb_paiements_sejours = paiements_sejours.count()
    total_paiements_sejours = paiements_sejours.aggregate(Sum('montant_restant'))
    # Partie caution
    cautions_materiel = Adoption.objects.filter(date_caution_materiel__gte=today).filter \
        (date_caution_materiel__lte=interval_month).count()
    cautions_sterilisation = Adoption.objects.filter(date_caution_sterilisation__gte=today).filter \
        (date_caution_sterilisation__lte=interval_month).count()
    #Animaux refuge a steriliser ou vacciner
    nb_visites_refuge = Animal.objects.filter(
        Q(emplacement=EmplacementChoice.REFUGE.name),
        Q(vaccine=OuiNonChoice.NON.name)|
        Q(sterilise=OuiNonChoice.NON.name)
    ).count()
    #Animaux pension a vacciner
    nb_vaccinations = Animal.objects.filter(
        Q(emplacement=EmplacementChoice.PENSION.name),
        Q(date_visite__lte=today)
    ).count()

    #Données du planning de la semaine
    sejours = Sejour.objects.all()
    date_planning = timezone.now().date()
    interval_planning = timezone.now().date() + timedelta(days=1)

    labels_planning = []
    data_planning = []
    couleurs_planning = []
    urls = []

    i = 1
    while (i < 20):
        urls.append(reverse('sejours') + "?interval="+date_planning.strftime("%Y-%m-%d")+"&filter=date_sejour")
        labels_planning.append(date_planning.strftime("%d/%m"))
        count = sejours.filter(date_arrivee__lte=interval_planning).filter(date_depart__gte=date_planning) \
            .filter(annule=False) \
            .aggregate(total = Sum(F('nb_cages_fournies') + F('nb_cages_a_fournir'))).get("total")
        count = count if count else 0
        data_planning.append(count)
        color_count = count if count < 33 else 33
        couleurs_planning.append("hsl(" + str(100 - 3 * color_count) + ",70%,50%)")
        date_planning = date_planning + timedelta(days=1)
        interval_planning = interval_planning + timedelta(days=1)
        i += 1
    urls_string = ','.join(urls)
    return render(request, "admin_interface/tableau_bord.html", locals())

@login_required
def stats(request):

    selected = "statistiques"

    date = timezone.now().date()

    if request.method == "POST":
        form = SejourStatsForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data["date_debut"]
    else:
        form = SejourStatsForm()

    #Partie planning
    sejours = Sejour.objects.all()
    interval = date + timedelta(days=1)

    labels_planning = []
    data_planning = []
    couleurs_planning = []
    urls = []

    i = 1
    while (i < 40):
        labels_planning.append(date.strftime("%d/%m"))
        urls.append(reverse('sejours') + "?interval="+date.strftime("%Y-%m-%d")+"&filter=date_sejour")
        count = sejours.filter(date_arrivee__lte=interval).filter(date_depart__gte=date)\
            .filter(annule=False)\
            .aggregate(total = Sum(F('nb_cages_fournies') + F('nb_cages_a_fournir'))).get("total")
        count = count if count else 0
        data_planning.append(count)
        color_count = count if count < 33 else 33
        couleurs_planning.append("hsl(" + str(100-3*color_count) + ",70%,50%)")
        date = date + timedelta(days=1)
        interval = interval + timedelta(days=1)
        i+=1

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

    pensions_calculees = Sejour.objects.filter(date_arrivee__year=date.year).filter(annule=False).\
                             values('proprietaire__user__last_name','proprietaire__user__first_name'). \
        annotate(total_pensions=Sum('nb_jours')).order_by('-total_pensions')[:5]
    palmares = []

    for pension in pensions_calculees:
        palmares.insert(0,DotDict(pension))
    palmares.reverse()

    urls_string = ','.join(urls)

    return render(request, "admin_interface/statistiques.html", {
        'labels_adoption':labels_adoption,
        'data_adoption_current':data_adoption_current,
        'data_adoption_past': data_adoption_past,
        'selected':selected,
        'current':date.year,
        'urls_string': urls_string,
        'past': date.year-1,
        'form': form,
        'palmares':palmares,
        'labels_planning':labels_planning,
        'data_planning':data_planning,
        'couleurs_planning':couleurs_planning

    })

class DotDict( dict):
    def __getattr__( self, attr):
        return self[attr] # or, return self.get( attr, default_value)