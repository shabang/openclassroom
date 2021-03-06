import sys
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.generic import CreateView, UpdateView

from admin_interface.forms.sejours import SejourForm, SejourSearchForm
from admin_interface.models import OuiNonChoice, TypeSupplementChoice
from admin_interface.models.animaux import Animal
from admin_interface.models.proprietaires import Proprietaire
from admin_interface.models.sejours import Sejour
from admin_interface.models.tarifs import ParametreTarifairePension, TarifJournalier
from admin_interface.utils import is_time_between


class CreateSejour(LoginRequiredMixin, CreateView):
    model = Sejour
    template_name = "admin_interface/sejour_form.html"
    form_class = SejourForm

    def get_form(self, form_class=None):
        form = CreateView.get_form(self, form_class=form_class)
        id_proprietaire = self.request.GET.get("proprietaire", "")
        if id_proprietaire:
            proprietaire = Proprietaire.objects.get(id=id_proprietaire)
            form.fields["proprietaire"].initial = proprietaire
            form.fields["animaux"].queryset = Animal.objects.filter(
                proprietaire_id=id_proprietaire
            ).filter(inactif=False).order_by("nom")
        return form

    def get_success_url(self):
        return reverse_lazy("detail_sejour", kwargs={"pk": self.object.id})


class UpdateSejour(LoginRequiredMixin, UpdateView):
    model = Sejour
    template_name = "admin_interface/sejour_form.html"
    form_class = SejourForm

    def get_form(self, form_class=None):
        form = UpdateView.get_form(self, form_class=form_class)
        sejour = self.object
        proprietaire = sejour.proprietaire
        form.fields["animaux"].queryset = Animal.objects.filter(
            proprietaire_id=proprietaire.id
        ).order_by("nom")
        return form

    def get_success_url(self):
        return reverse_lazy("detail_sejour", kwargs={"pk": self.object.id})


@login_required
def search_sejour(request):
    selected = "sejours"
    sejours = Sejour.objects.all().filter(annule=False)

    if request.method == "POST":
        form = SejourSearchForm(request.POST)
        if form.is_valid():
            base_url = reverse('sejours')
            query_string = form.data.urlencode()
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    else:
        form = SejourSearchForm()

        date_debut_min_form = request.GET.get("date_debut_min", "")
        date_debut_max_form = request.GET.get("date_debut_max", "")
        date_fin_min_form = request.GET.get("date_fin_min", "")
        date_fin_max_form = request.GET.get("date_fin_max", "")
        proprietaire_form = request.GET.get("proprietaire", "")
        cohabitation_form = request.GET.get("cohabitation", "")
        animal_form = request.GET.get("animal","")

        if animal_form:
            sejours = sejours.filter(animaux__id=animal_form)
            form.fields["animal"].initial = animal_form
        if date_debut_min_form:
            sejours = sejours.filter(date_arrivee__gte=parse_date(date_debut_min_form))
            form.fields["date_debut_min"].initial = date_debut_min_form
        if date_debut_max_form:
            sejours = sejours.filter(date_arrivee__lte=parse_date(date_debut_max_form))
            form.fields["date_debut_max"].initial = date_debut_max_form
        if date_fin_min_form:
            sejours = sejours.filter(date_depart__gte=parse_date(date_fin_min_form))
            form.fields["date_fin_min"].initial = date_fin_min_form
        if date_fin_max_form:
            sejours = sejours.filter(date_depart__lte=parse_date(date_fin_max_form))
            form.fields["date_fin_max"].initial = date_fin_max_form
        if proprietaire_form:
            sejours = sejours.filter(proprietaire=proprietaire_form)
            form.fields["proprietaire"].initial = proprietaire_form
        if cohabitation_form:
            sejours = sejours.filter(cohabitation=cohabitation_form)
            form.fields["cohabitation"].initial = cohabitation_form

        # Param??tres de l'url pour filtres par d??faut
        filter_data = request.GET.get("filter", "")
        if filter_data:
            if filter_data == "paiements_sejour":
                sejours = sejours.filter(montant_restant__gt=Decimal('0'))

    #loading des objets li??s pour am??liorer la perf
    sejours = sejours.select_related('proprietaire').prefetch_related('animaux')
    # Pagination : 10 ??l??ments par page
    paginator = Paginator(sejours.order_by('-date_mise_a_jour'), 10)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        sejours = paginator.page(page)
    except EmptyPage:
        # Si on d??passe la limite de pages, on prend la derni??re
        sejours = paginator.page(paginator.num_pages())

    return render(request, "admin_interface/sejour_list.html", locals())


@login_required
def calcul_montant_sejour(request):
    montant_sejour = Decimal(0)
    # Inutile de calculer le montant si les donn??es ne sont pas correctement remplies
    # On commence donc par v??rifier toutes les donn??es essentielles au calcul
    try:
        date_arrivee = datetime.strptime(request.POST["date_arrivee_0"], "%d/%m/%Y")
        heure_arrivee = datetime.strptime(request.POST["date_arrivee_1"], "%H:%M").time()
        date_depart = datetime.strptime(request.POST["date_depart_0"], "%d/%m/%Y")
        heure_depart = datetime.strptime(request.POST["date_depart_1"], "%H:%M").time()
    except ValueError:
        # Si les champs sont mal remplis, on arrete le calcul
        return JsonResponse({"montant": montant_sejour})
    longue_duree = request.POST["longue_duree"]
    montant_jour_longue_duree = request.POST["montant_jour_longue_duree"]
    if (longue_duree and longue_duree=="OUI" and montant_jour_longue_duree):
        nb_jours = Decimal(abs((date_depart - date_arrivee).days)) + 1
        return JsonResponse({"montant": Decimal(montant_jour_longue_duree) * Decimal(nb_jours)
                                , "calcul": "Calcul longue dur??e"})
    nb_cages_a_fournir = request.POST["nb_cages_a_fournir"]
    nb_cages_fournies = request.POST["nb_cages_fournies"]
    proprietaire_input = request.POST["proprietaire"]
    arrhes_str = request.POST["arrhes"]
    calcul = ""
    if not (
        date_arrivee
        and heure_arrivee
        and date_depart
        and heure_depart
        and nb_cages_a_fournir
        and nb_cages_fournies
        and proprietaire_input
    ):
        # Si on a pas les donn??es pour faire le calcul le montant reste ?? 0
        return JsonResponse({"montant": montant_sejour})
    else:
        nb_jours = Decimal(abs((date_depart - date_arrivee).days)) + 1
        nb_cages = int(nb_cages_fournies) + int(nb_cages_a_fournir)
        animaux = Animal.objects.filter(id__in=request.POST.getlist("animaux")).order_by('-adoption')
        proprietaire = Proprietaire.objects.get(id=proprietaire_input)
        cohabitation = request.POST["cohabitation"]
        if cohabitation and cohabitation == OuiNonChoice.OUI.name:
            animaux = Animal.objects.filter(id__in=request.POST.getlist("animaux"))
            if animaux.count() > 1:
                tarif_j = ParametreTarifairePension.objects.get(
                    type_supplement=TypeSupplementChoice.COHABITATION_FORCEE.name
                )
            else:
                tarif_j = ParametreTarifairePension.objects.get(
                    type_supplement=TypeSupplementChoice.COHABITATION_LIBRE.name
                )

            montant_sejour = montant_sejour + (tarif_j.montant * nb_jours)
        else:
            try:
            # On commence par calculer le prix pour chaque animal
                for i, animal in enumerate(animaux):
                    adopte_refuge = (
                        OuiNonChoice.OUI.name
                        if animal.is_adopted_refuge()
                        else OuiNonChoice.NON.name
                    )
                    if i < nb_cages:
                        tarif_j = TarifJournalier.objects.get(
                            Q(type_animal=animal.type_animal)
                            & Q(supplementaire=OuiNonChoice.NON.name)
                            & Q(adopte_refuge=adopte_refuge)
                            & Q(tarif_special=proprietaire.tarif_special)
                        )
                    else:
                        tarif_j = TarifJournalier.objects.get(
                            Q(type_animal=animal.type_animal)
                            & Q(supplementaire=OuiNonChoice.OUI.name)
                            & Q(adopte_refuge=adopte_refuge)
                            & Q(tarif_special=proprietaire.tarif_special)
                        )
                    montant_sejour = montant_sejour + (tarif_j.montant_jour * nb_jours)
                    calcul += "<br/>"
                    calcul += "Tarif journalier : "
                    calcul += str(tarif_j.montant_jour)
                    calcul += "<br/> Nb jours du s??jour : "
                    calcul += str(nb_jours)
                    calcul += "<br/>"
                    calcul += "Montant total apr??s application du tarif journalier : "
                    calcul += str(montant_sejour)
                    calcul += "<br/>"

            except TarifJournalier.DoesNotExist:
                return JsonResponse({"montant": montant_sejour})
            # Ensuite, on calcule les suppl??ments
            supplement_cage = ParametreTarifairePension.objects.get(type_supplement="CAGE")
            montant_sejour = montant_sejour + (
                supplement_cage.montant * Decimal(nb_cages_a_fournir) * nb_jours
            )
            calcul += "<br/>"
            calcul += "Montant apr??s suppl??ment cage : "
            calcul += str(montant_sejour)
            injection = request.POST["injection"]
            soin = request.POST["soin"]
            vaccination = request.POST["vaccination"]
            # Suppl??ment soin par voie orale ou par injection
            if injection and injection == OuiNonChoice.OUI.name:
                supplement_injection = ParametreTarifairePension.objects.get(
                    type_supplement=TypeSupplementChoice.INJECTION.name
                )
                montant_sejour = montant_sejour + (supplement_injection.montant * nb_jours)
            elif soin and soin == OuiNonChoice.OUI.name:
                supplement_soin = ParametreTarifairePension.objects.get(
                    type_supplement=TypeSupplementChoice.MEDICAMENT.name
                )
                montant_sejour = montant_sejour + (supplement_soin.montant * nb_jours)
            calcul += "<br/>"
            calcul += "Montant apr??s suppl??ment soin : "
            calcul += str(montant_sejour)
            # Suppl??ment vaccination
            if vaccination and vaccination == OuiNonChoice.NON.name:
                supplement_vaccination = ParametreTarifairePension.objects.get(
                    type_supplement=TypeSupplementChoice.VACCINATION.name
                )
                montant_sejour = montant_sejour + supplement_vaccination.montant
            calcul += "<br/>"
            calcul += "Montant apr??s suppl??ment vaccination : "
            calcul += str(montant_sejour)
        # Suppl??ment samedi ou suppl??ment horaire
        supplement_samedi = ParametreTarifairePension.objects.get(
            type_supplement=TypeSupplementChoice.SAMEDI.name
        )
        supplement_horaire = ParametreTarifairePension.objects.get(
            type_supplement=TypeSupplementChoice.HORAIRE.name
        )
        if date_arrivee.weekday() == 6:
            montant_sejour = montant_sejour + supplement_samedi.montant
            calcul += "<br/> Ajout suppl??ment arriv??e dimanche"
        elif date_arrivee.weekday() in (0, 1, 3, 4) and not is_time_between(
            time(17, 59), time(19, 31), heure_arrivee
        ):
            montant_sejour = montant_sejour + supplement_horaire.montant
            calcul += "<br/> Ajout suppl??ment horaire arriv??e"
        elif date_arrivee.weekday() in (2, 5) and not is_time_between(
            time(14, 59), time(18, 31), heure_arrivee
        ):
            montant_sejour = montant_sejour + supplement_horaire.montant
            calcul += "<br/> Ajout suppl??ment horaire arriv??e"
        if date_depart.weekday() == 6:
            montant_sejour = montant_sejour + supplement_samedi.montant
            calcul += "<br/> Ajout suppl??ment dimanche d??part"
        elif date_depart.weekday() in (0, 1, 3, 4) and not is_time_between(
            time(17, 59), time(19, 31), heure_depart
        ):
            montant_sejour = montant_sejour + supplement_horaire.montant
            calcul += "<br/> Ajout suppl??ment horaire d??part"
        elif date_depart.weekday() in (2, 5) and not is_time_between(
            time(14, 59), time(18, 31), heure_depart
        ):
            montant_sejour = montant_sejour + supplement_horaire.montant
            calcul += "<br/> Ajout suppl??ment horaire d??part"
        calcul += "<br/>"

        calcul += "Montant total : "
        calcul += str(montant_sejour)
        calcul += "<br/>"
        calcul += "<br/>"
        montant_restant = montant_sejour
        if (arrhes_str):
            arrhes = Decimal(arrhes_str)
            montant_restant = montant_restant - arrhes

    # Renvoyer vue json
    return JsonResponse({"montant": montant_sejour, "calcul": calcul, "montant_restant": montant_restant})

@login_required
def annule_sejour(request, sejour_id):
    sejour = Sejour.objects.get(id=sejour_id)
    sejour.annulation()
    sejour.save()
    return redirect("detail_sejour", pk=sejour_id)

@login_required
def paye_sejour(request, sejour_id):
    sejour = Sejour.objects.get(id=sejour_id)
    sejour.montant_restant = 0;
    sejour.save()
    return redirect("detail_sejour", pk=sejour_id)
