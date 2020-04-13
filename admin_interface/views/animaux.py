
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.generic import CreateView, UpdateView

from admin_interface.forms import AnimalCreateForm, AnimalSearchForm, AnimalUpdateForm
from admin_interface.models import EmplacementChoice
from admin_interface.models.animaux import Animal
from admin_interface.models.proprietaires import Proprietaire


class CreateAnimal(LoginRequiredMixin, CreateView):
    model = Animal
    form_class = AnimalCreateForm
    template_name = 'admin_interface/animal_form.html'

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

    template_name = 'admin_interface/animal_form.html'

    def get_success_url(self):
        return reverse_lazy('detail_animal', kwargs={'pk': self.object.id})


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

    return render(request, 'admin_interface/animal_list.html', locals())


@login_required
def load_animals(request):
    proprietaire_id = request.GET.get('proprietaire')
    animaux = Animal.objects.filter(proprietaire_id=proprietaire_id)
    return render(request, 'admin_interface/sejour_form_select_animals.html', {'animaux': animaux})
