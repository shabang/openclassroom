# -*- coding: utf-8 -*-
import sys
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView
from applicationTest.forms import AnimalSearchForm, ProprietaireSearchForm, AnimalUpdateForm, \
    AnimalCreateForm, ConnexionForm, VisiteSearchForm, SejourSearchForm, UserForm, ProprietaireForm, SejourForm, \
    AdoptionFormNoProprietaire, AdoptionForm, AdoptionUpdateForm
from applicationTest.models import Animal, Proprietaire, VisiteMedicale, Sejour, \
    Adoption, TarifJournalier, TarifAdoption, ParametreTarifairePension, \
    TypeSupplementChoice, OuiNonChoice, EmplacementChoice
from django.urls import reverse_lazy
from _datetime import timedelta, datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.utils.dateparse import parse_date
from django.core.exceptions import ObjectDoesNotExist


def connexion(request):
    error = False
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect("accueil")
            else:
                error = True
    else:
        form = ConnexionForm()
    return render(request, 'applicationTest/login.html', locals())


@permission_required('applicationTest.view_animal')
def home(request):
    # Pour la sidebar
    selected = "tableau_bord"

    # Dates
    today = timezone.now()
    interval = timezone.now() + timedelta(days=7)
    interval_str = interval.strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    # Partie pension
    arrivees_pension = Sejour.objects.filter(date_arrivee__gt=today).filter(date_arrivee__lt=interval).count()
    departs_pension = Sejour.objects.filter(date_depart__gt=today).filter(date_depart__lt=interval).count()
    presences = Sejour.objects.filter(date_arrivee__lt=today).filter(date_depart__gt=today).count()
    # Partie refuge
    rdv_veterinaire = Animal.objects.filter(emplacement=EmplacementChoice.REFUGE.name).filter(date_visite__gt=today).filter(
        date_visite__lt=interval).count()
    recuperations = Animal.objects.filter(emplacement=EmplacementChoice.REFUGE.name).filter(date_arrivee__gt=today).filter(
        date_arrivee__lt=interval).count()
    adoptions = Adoption.objects.filter(date__gt=today).filter(date__lt=interval).count()

    return render(request, 'applicationTest/tableau_bord.html', locals())


class CreateAnimal(LoginRequiredMixin, CreateView):
    model = Animal
    form_class = AnimalCreateForm
    template_name = 'applicationTest/animal_form.html'

    def get_form(self, form_class=None):
        form = CreateView.get_form(self, form_class=form_class)
        id_proprietaire = self.request.GET.get('proprietaire', '')
        if id_proprietaire:
            proprietaire = Proprietaire.objects.get(id=id_proprietaire)
            form.fields['proprietaire'].initial = proprietaire
            form.fields['emplacement'].initial = EmplacementChoice.PENSION.name
        return form

    def get_success_url(self):
        return reverse_lazy('detail_animal', kwargs={'pk': self.object.id})


class UpdateAnimal(LoginRequiredMixin, UpdateView):
    model = Animal
    form_class = AnimalUpdateForm

    template_name = 'applicationTest/animal_form.html'

    def get_success_url(self):
        return reverse_lazy('detail_animal', kwargs={'pk': self.object.id})


@login_required
def create_proprietaire(request):
    formulaire_valide = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        proprietaire_form = ProprietaireForm(data=request.POST)
        if user_form.is_valid() and proprietaire_form.is_valid():
            # A l'enregistreent de l'utilisateur, identifiant et mot de passe sont autaumatiquement calculés
            user = user_form.save()

            proprietaire = proprietaire_form.save(commit=False)
            proprietaire.user = user
            proprietaire.save()

            formulaire_valide = True
            return redirect('detail_proprietaire', pk=proprietaire.id)

    else:
        user_form = UserForm()
        proprietaire_form = ProprietaireForm()
    # Render the template depending on the context.
    return render(request, 'applicationTest/proprietaire_form.html', locals())


@login_required
def update_proprietaire(request, pk):
    proprietaire_to_update = Proprietaire.objects.get(id=pk)

    if request.method == 'POST':
        user_form = UserForm(data=request.POST, instance=proprietaire_to_update.user)
        proprietaire_form = ProprietaireForm(data=request.POST, instance=proprietaire_to_update)
        if user_form.is_valid() and proprietaire_form.is_valid():
            user = user_form.save()
            proprietaire = proprietaire_form.save()
            return redirect('detail_proprietaire', pk=pk)

    else:
        user_form = UserForm(instance=proprietaire_to_update.user)
        proprietaire_form = ProprietaireForm(instance=proprietaire_to_update)
    # Render the template depending on the context.
    return render(request, 'applicationTest/proprietaire_form.html', locals())


class CreateVisite(LoginRequiredMixin, CreateView):
    model = VisiteMedicale
    template_name = 'applicationTest/visite_form.html'
    fields = ('date', 'type_visite', 'montant', 'animaux', 'commentaire')
    success_url = reverse_lazy('visites')

    def get_form(self, form_class=None):
        form = CreateView.get_form(self, form_class=form_class)
        form.fields['animaux'].queryset = Animal.objects.filter(emplacement=EmplacementChoice.REFUGE.name)
        return form


class UpdateAdoption(LoginRequiredMixin, UpdateView):
    model = Adoption
    template_name = 'applicationTest/update_adoption.html'
    form_class = AdoptionUpdateForm

    def get_success_url(self):
        return reverse_lazy('detail_animal', kwargs={'pk': self.object.animal.id})


class CreateSejour(LoginRequiredMixin, CreateView):
    model = Sejour
    template_name = 'applicationTest/sejour_form.html'
    form_class = SejourForm

    def get_form(self, form_class=None):
        form = CreateView.get_form(self, form_class=form_class)
        id_proprietaire = self.request.GET.get('proprietaire', '')
        if id_proprietaire:
            proprietaire = Proprietaire.objects.get(id=id_proprietaire)
            form.fields['proprietaire'].initial = proprietaire
            form.fields['animaux'].queryset = Animal.objects.filter(proprietaire_id=id_proprietaire).order_by('nom')
        return form

    def get_success_url(self):
        return reverse_lazy('detail_sejour', kwargs={'pk': self.object.id})


class UpdateSejour(LoginRequiredMixin, UpdateView):
    model = Sejour
    template_name = 'applicationTest/sejour_form.html'
    form_class = SejourForm

    def get_form(self, form_class=None):
        form = UpdateView.get_form(self, form_class=form_class)
        sejour = self.object
        proprietaire = sejour.proprietaire
        form.fields['animaux'].queryset = Animal.objects.filter(proprietaire_id=proprietaire.id).order_by('nom')
        return form

    def get_success_url(self):
        return reverse_lazy('detail_sejour', kwargs={'pk': self.object.id})


@login_required
def search_animal(request):
    animals = Animal.objects.all()
    selected = "animals"

    if request.method == 'POST':
        form = AnimalSearchForm(request.POST)
        if form.is_valid():

            proprietaire_form = form.cleaned_data['proprietaire']
            type_animal_form = form.cleaned_data['type_animal']
            nom_form = form.cleaned_data['nom']
            provenance_form = form.cleaned_data['emplacement']
            date_naissance_min = form.cleaned_data['date_naissance_min']
            date_naissance_max = form.cleaned_data['date_naissance_max']
            date_arrivee_min = form.cleaned_data['date_arrivee_min']
            date_arrivee_max = form.cleaned_data['date_arrivee_max']
            date_prochaine_visite_min = form.cleaned_data['date_prochaine_visite_min']
            date_prochaine_visite_max = form.cleaned_data['date_prochaine_visite_max']
            date_adoption_min = form.cleaned_data['date_adoption_min']
            date_adoption_max = form.cleaned_data['date_adoption_max']

            if proprietaire_form is not None:
                animals = animals.filter(proprietaire=proprietaire_form)
            if provenance_form:
                animals = animals.filter(emplacement=provenance_form)
            if type_animal_form:
                animals = animals.filter(type_animal=type_animal_form)
            if nom_form is not None:
                animals = animals.filter(nom__icontains=nom_form)
            if date_naissance_min:
                animals = animals.filter(date_naissance__gte=date_naissance_min)
            if date_naissance_max:
                animals = animals.filter(date_naissance__lte=date_naissance_max)
            if date_arrivee_min:
                animals = animals.filter(date_arrivee__gte=date_arrivee_min)
            if date_arrivee_max:
                animals = animals.filter(date_arrivee__lte=date_arrivee_max)
            if date_prochaine_visite_min:
                animals = animals.filter(date_visite__gte=date_prochaine_visite_min)
            if date_prochaine_visite_max:
                animals = animals.filter(date_visite__lte=date_prochaine_visite_max)
    else:
        form = AnimalSearchForm()
        # Paramètres de l'url pour filtres par défaut
        interval_str = request.GET.get('interval', '')
        filter_data = request.GET.get('filter', '')
        if filter_data:

            interval = parse_date(interval_str)
            today = timezone.now()
            today_str = today.strftime('%Y-%m-%d')

            if filter_data == "date_visite":
                form.fields['date_prochaine_visite_max'].initial = interval_str
                form.fields['date_prochaine_visite_min'].initial = today_str
                animals = animals.filter(date_visite__gte=today)
                animals = animals.filter(date_visite__lte=interval)
            if filter_data == "date_arrivee":
                form.fields['date_arrivee_max'].initial = interval_str
                form.fields['date_arrivee_min'].initial = today_str
                animals = animals.filter(date_arrivee__gte=today)
                animals = animals.filter(date_arrivee__lte=interval)
            if filter_data == "date_adoption":
                form.fields['date_adoption_max'].initial = interval_str
                form.fields['date_adoption_min'].initial = today_str
                animals = animals.filter(adoption__date__gte=today)
                animals = animals.filter(adoption__date__lte=interval)
            if filter_data == "pension":
                form.fields['emplacement'].initial = EmplacementChoice.PENSION.name
                animals = animals.filter(emplacement=EmplacementChoice.PENSION.name)
            if filter_data == "refuge":
                form.fields['emplacement'].initial = EmplacementChoice.REFUGE.name
                animals = animals.filter(emplacement=EmplacementChoice.REFUGE.name)

    return render(request, 'applicationTest/animal_list.html', locals())


@login_required
def search_proprietaire(request):
    selected = "proprietaires"
    proprietaires = Proprietaire.objects.all()

    if request.method == 'POST':
        form = ProprietaireSearchForm(request.POST)
        if form.is_valid():

            nom_form = form.cleaned_data['nom']

            if nom_form is not None:
                proprietaires = proprietaires.filter(nom__icontains=nom_form)
    else:
        form = ProprietaireSearchForm()
    return render(request, 'applicationTest/proprietaire_list.html', locals())


@login_required
def search_visite(request):
    selected = "visites"
    visites = VisiteMedicale.objects.all()

    if request.method == 'POST':
        form = VisiteSearchForm(request.POST)
        if form.is_valid():

            date_min_form = form.cleaned_data['date_min']
            date_max_form = form.cleaned_data['date_max']

            if date_min_form:
                visites = visites.filter(date__gte=date_min_form)
            if date_max_form:
                visites = visites.filter(date__lte=date_max_form)

    else:
        form = VisiteSearchForm()

    return render(request, 'applicationTest/visite_list.html', locals())


@login_required
def search_sejour(request):
    selected = "sejours"
    sejours = Sejour.objects.all()

    if request.method == 'POST':
        form = SejourSearchForm(request.POST)
        if form.is_valid():

            date_debut_min_form = form.cleaned_data['date_debut_min']
            date_debut_max_form = form.cleaned_data['date_debut_max']
            date_fin_min_form = form.cleaned_data['date_fin_min']
            date_fin_max_form = form.cleaned_data['date_fin_max']
            proprietaire_form = form.cleaned_data['proprietaire']

            if date_debut_min_form:
                sejours = sejours.filter(date_arrivee__gte=date_debut_min_form)
            if date_debut_max_form:
                sejours = sejours.filter(date_arrivee__lte=date_debut_max_form)
            if date_fin_min_form:
                sejours = sejours.filter(date_depart__gte=date_fin_min_form)
            if date_fin_max_form:
                sejours = sejours.filter(date_depart__lte=date_fin_max_form)
            if proprietaire_form is not None:
                sejours = sejours.filter(proprietaire=proprietaire_form)
    else:
        form = SejourSearchForm()

        # Paramètres de l'url pour filtres par défaut
        interval_str = request.GET.get('interval', '')
        filter_data = request.GET.get('filter', '')
        if filter:

            interval = parse_date(interval_str)
            today = timezone.now()
            today_str = today.strftime('%Y-%m-%d')

            if filter_data == "date_debut_sejour":
                form.fields['date_debut_max'].initial = interval_str
                form.fields['date_debut_min'].initial = today_str
                sejours = sejours.filter(date_arrivee__gte=today)
                sejours = sejours.filter(date_arrivee__lte=interval)
            if filter_data == "date_fin_sejour":
                form.fields['date_fin_max'].initial = interval_str
                form.fields['date_fin_min'].initial = today_str
                sejours = sejours.filter(date_depart__gte=today)
                sejours = sejours.filter(date_depart__lte=interval)
            if filter_data == "date_sejour":
                form.fields['date_fin_min'].initial = interval_str
                form.fields['date_debut_max'].initial = today_str
                sejours = sejours.filter(date_depart__gte=interval)
                sejours = sejours.filter(date_arrivee__lte=today)

    return render(request, 'applicationTest/sejour_list.html', locals())


@login_required
def load_animals(request):
    proprietaire_id = request.GET.get('proprietaire')
    animaux = Animal.objects.filter(proprietaire_id=proprietaire_id)
    return render(request, 'applicationTest/sejour_form_select_animals.html', {'animaux': animaux})


@login_required
def calcul_montant_sejour(request):
    montant_sejour = Decimal(0)
    # Inutile de calculer le montant si les données ne sont pas correctement remplies
    # On commence donc par vérifier toutes les données essentielles au calcul
    date_arrivee = datetime.strptime(request.POST["date_arrivee_0"], '%d/%m/%Y')
    heure_arrivee = request.POST["date_arrivee_1"]
    date_depart = datetime.strptime(request.POST["date_depart_0"], '%d/%m/%Y')
    heure_depart = request.POST["date_depart_1"]
    nb_cages_a_fournir = request.POST["nb_cages_a_fournir"]
    nb_cages_fournies = request.POST["nb_cages_fournies"]
    if not nb_cages_fournies:
        test = "test"
    if not (date_arrivee and heure_arrivee and date_depart and
            heure_depart and nb_cages_a_fournir and nb_cages_fournies):
        # Si on a pas les données pour faire le calcul le montant reste à 0
        return JsonResponse({'montant': montant_sejour})
    else:
        nb_jours = Decimal(abs((date_depart - date_arrivee).days))
        nb_cages = int(nb_cages_fournies) + int(nb_cages_a_fournir)
        animaux = request.POST.getlist("animaux")
        # On commence par calculer le prix pour chaque animal
        for i, elt in enumerate(animaux):
            animal = Animal.objects.get(id=elt)
            adopte_refuge = OuiNonChoice.OUI.name if animal.is_adopted_refuge() else OuiNonChoice.NON.name
            if i < nb_cages:
                tarif_j = TarifJournalier.objects.get(Q(type_animal=animal.type_animal) &
                                                      Q(supplementaire=OuiNonChoice.NON.name) & Q(
                    adopte_refuge=adopte_refuge))
            else:
                tarif_j = TarifJournalier.objects.get(Q(type_animal=animal.type_animal) &
                                                      Q(supplementaire=OuiNonChoice.OUI.name) & Q(
                    adopte_refuge=adopte_refuge))
            montant_sejour = montant_sejour + (tarif_j.montant_jour * nb_jours)
        # Ensuite, on calcule les suppléments
        supplement_cage = ParametreTarifairePension.objects.get(type_supplement="CAGE")
        montant_sejour = montant_sejour + (supplement_cage.montant * Decimal(nb_cages_a_fournir) * nb_jours)
        injection = request.POST["injection"]
        soin = request.POST["soin"]
        vaccination = request.POST["vaccination"]
        if injection and injection == OuiNonChoice.OUI.name:
            supplement_injection = ParametreTarifairePension.objects.get(
                type_supplement=TypeSupplementChoice.INJECTION.name)
            montant_sejour = montant_sejour + (supplement_injection.montant * nb_jours)
        elif soin and soin == OuiNonChoice.OUI.name:
            supplement_soin = ParametreTarifairePension.objects.get(
                type_supplement=TypeSupplementChoice.MEDICAMENT.name)
            montant_sejour = montant_sejour + (supplement_soin.montant * nb_jours)
        if vaccination and vaccination == OuiNonChoice.OUI.name:
            supplement_vaccination = ParametreTarifairePension.objects.get(
                type_supplement=TypeSupplementChoice.VACCINATION.name)
            montant_sejour = montant_sejour + supplement_vaccination.montant
        supplement_samedi = ParametreTarifairePension.objects.get(type_supplement=TypeSupplementChoice.SAMEDI.name)
        # TODO : manque partie horaire
        if date_arrivee.weekday() == 5:
            montant_sejour = montant_sejour + supplement_samedi.montant
        if date_depart.weekday() == 5:
            montant_sejour = montant_sejour + supplement_samedi.montant

    sys.stdout.flush()

    # Recuperer les parametres tarifaires
    # Calcul du montant du séjour
    # Renvoyer vue json
    return JsonResponse({'montant': montant_sejour})


@login_required
def parametrage_tarifaire(request):
    selected = "parametrage_tarifaire"
    tarifs_journaliers_pension = TarifJournalier.objects.all()
    tarifs_supplements = ParametreTarifairePension.objects.all()
    tarifs_adoption = TarifAdoption.objects.all()
    return render(request, 'applicationTest/parametrage_tarifaire.html', locals())


@login_required
def adoption(request, pk):
    animal = Animal.objects.get(id=pk)
    return render(request, 'applicationTest/adoption.html', locals())


@login_required
def adoption_complete(request, pk):
    animal = Animal.objects.get(id=pk)
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        proprietaire_form = ProprietaireForm(data=request.POST)
        adoption_form = AdoptionFormNoProprietaire(data=request.POST)
        if user_form.is_valid() and proprietaire_form.is_valid() and adoption_form.is_valid():
            # A l'enregistreent de l'utilisateur, identifiant et mot de passe sont autaumatiquement calculés
            user = user_form.save()

            proprietaire = proprietaire_form.save(commit=False)
            proprietaire.user = user
            proprietaire.save()

            # On rattache le nouveau proprietaire à l'adoption
            adoption = adoption_form.save(commit=False)
            adoption.proprietaire = proprietaire
            adoption.animal = animal
            adoption.save()

            # l'animal ne fait plus partie du refuge
            animal.emplacement = EmplacementChoice.PENSION.name
            animal.proprietaire = proprietaire
            animal.save()

            return redirect('detail_animal', pk=animal.id)

    else:
        user_form = UserForm()
        proprietaire_form = ProprietaireForm()
        adoption_form = AdoptionFormNoProprietaire()
        montant_adoption = get_montant_adoption(animal)
        if montant_adoption:
            adoption_form.fields['montant'].initial = montant_adoption
            adoption_form.fields['montant_restant'].initial = montant_adoption

    return render(request, 'applicationTest/adoption_complete.html', locals())


@login_required
def adoption_allegee(request, pk):
    animal = Animal.objects.get(id=pk)
    if request.method == 'POST':
        adoption_form = AdoptionForm(data=request.POST)
        if adoption_form.is_valid():
            # On rattache le nouveau proprietaire à l'adoption
            new_adoption = adoption_form.save(commit=False)

            # l'animal ne fait plus partie du refuge
            new_adoption.animal = animal
            new_adoption.save()
            animal.emplacement = EmplacementChoice.PENSION.name
            animal.proprietaire = adoption.proprietaire
            animal.save()

            return redirect('detail_animal', pk=animal.id)

    else:
        adoption_form = AdoptionForm()
        montant_adoption = get_montant_adoption(animal)
        adoption_form.fields['montant'].initial = montant_adoption
        adoption_form.fields['montant_restant'].initial = montant_adoption
    return render(request, 'applicationTest/adoption_allegee.html', locals())


def get_montant_adoption(animal):
    try:
        tarif_applicable = TarifAdoption.objects.get(type_animal=animal.type_animal, sexe=animal.sexe,
                                                     sterilise=animal.sterilise)
        return tarif_applicable.montant_adoption
    except ObjectDoesNotExist:
        return None
