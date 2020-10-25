import sys
from decimal import Decimal

import os

import base64
import requests

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.generic import CreateView, UpdateView, FormView

from admin_interface.forms import UploadImageForm
from admin_interface.forms.animaux import AnimalCreateForm, AnimalUpdateForm, AnimalSearchForm
from admin_interface.models import EmplacementChoice, OuiNonChoice
from admin_interface.models.animaux import Animal
from admin_interface.models.proprietaires import Proprietaire
from les_grandes_oreilles import settings


class CreateAnimal(LoginRequiredMixin, CreateView):
    model = Animal
    form_class = AnimalCreateForm
    template_name = "admin_interface/animal_form.html"

    def get_form(self, form_class=None):
        form = CreateView.get_form(self, form_class=form_class)
        id_proprietaire = self.request.GET.get("proprietaire", "")
        if id_proprietaire:
            proprietaire = Proprietaire.objects.get(id=id_proprietaire)
            form.fields["proprietaire"].initial = proprietaire
            form.fields["emplacement"].initial = EmplacementChoice.PENSION.name
        return form

    def get_success_url(self):
        return reverse_lazy("detail_animal", kwargs={"pk": self.object.id})


class UpdateAnimal(LoginRequiredMixin, UpdateView):
    model = Animal
    form_class = AnimalUpdateForm

    template_name = "admin_interface/animal_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_animal", kwargs={"pk": self.object.id})


@login_required
def search_animal(request):
    animals = Animal.objects.filter(inactif=False)
    selected = "animals"

    if request.method == "POST":
        form = AnimalSearchForm(request.POST)
        if form.is_valid():

            proprietaire_form = form.cleaned_data["proprietaire"]
            emplacement_form = form.cleaned_data["emplacement"]
            type_animal_form = form.cleaned_data["type_animal"]
            nom_form = form.cleaned_data["nom"]
            date_naissance_min = form.cleaned_data["date_naissance_min"]
            date_naissance_max = form.cleaned_data["date_naissance_max"]
            date_arrivee_min = form.cleaned_data["date_arrivee_min"]
            date_arrivee_max = form.cleaned_data["date_arrivee_max"]
            date_prochaine_visite_min = form.cleaned_data["date_prochaine_visite_min"]
            date_prochaine_visite_max = form.cleaned_data["date_prochaine_visite_max"]
            date_adoption_min = form.cleaned_data["date_adoption_min"]
            date_adoption_max = form.cleaned_data["date_adoption_max"]

            if proprietaire_form is not None:
                animals = animals.filter(proprietaire=proprietaire_form)
            if emplacement_form:
                animals = animals.filter(emplacement=emplacement_form)
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
            if date_adoption_min:
                animals = animals.filter(adoption__date__gte=date_adoption_min)
            if date_adoption_max:
                animals = animals.filter(adoption__date__lte=date_adoption_max)
    else:
        form = AnimalSearchForm()
        # Paramètres de l'url pour filtres par défaut
        interval_str = request.GET.get("interval", "")
        filter_data = request.GET.get("filter", "")
        if filter_data:

            interval = parse_date(interval_str)
            today = timezone.now().date()
            today_str = today.strftime("%Y-%m-%d")

            if filter_data == "date_visite":
                form.fields["date_prochaine_visite_max"].initial = interval_str
                form.fields["date_prochaine_visite_min"].initial = today_str
                animals = animals.filter(date_visite__gte=today)
                animals = animals.filter(date_visite__lte=interval)
            elif filter_data == "date_arrivee":
                form.fields["date_arrivee_max"].initial = interval_str
                form.fields["date_arrivee_min"].initial = today_str
                animals = animals.filter(date_arrivee__gte=today)
                animals = animals.filter(date_arrivee__lte=interval)
            elif filter_data == "date_adoption":
                form.fields["date_adoption_max"].initial = interval_str
                form.fields["date_adoption_min"].initial = today_str
                animals = animals.filter(adoption__date__gte=today)
                animals = animals.filter(adoption__date__lte=interval)
            elif filter_data == "pension":
                form.fields["emplacement"].initial = EmplacementChoice.PENSION.name
                animals = animals.filter(emplacement=EmplacementChoice.PENSION.name)
            elif filter_data == "refuge":
                form.fields["emplacement"].initial = EmplacementChoice.REFUGE.name
                animals = animals.filter(emplacement=EmplacementChoice.REFUGE.name)
            elif filter_data == "paiements_adoption":
                animals = animals.filter(adoption__montant_restant__gt=Decimal('0'))
            elif filter_data == "pension_vaccin":
                animals = animals.filter(
                    Q(emplacement=EmplacementChoice.PENSION.name),
                    Q(date_visite__lt=today)
                )
            elif filter_data == "sante_refuge":
                animals = animals.filter(
                    Q(emplacement=EmplacementChoice.REFUGE.name),
                    Q(vaccine=OuiNonChoice.NON.name)|
                    Q(sterilise=OuiNonChoice.NON.name)
                )

    # Pagination : 10 éléments par page
    paginator = Paginator(animals.order_by('-date_mise_a_jour'), 10)
    try:
        page = request.GET.get("page")
        if not page :
            page = 1
        animal_list = paginator.page(page)
    except EmptyPage:
        # Si on dépasse la limite de pages, on prend la dernière
        animal_list = paginator.page(paginator.num_pages())
    return render(request, "admin_interface/animal_list.html", locals())


@login_required
def load_animals(request):
    proprietaire_id = request.GET.get("proprietaire")
    animaux = Animal.objects.filter(inactif=False).filter(proprietaire_id=proprietaire_id)
    return render(
        request, "admin_interface/sejour_form_select_animals.html", {"animaux": animaux}
    )

class ImageForm(LoginRequiredMixin, FormView):
    template_name = 'admin_interface/wp_image_form.html'
    form_class = UploadImageForm

    def get_success_url(self):
        return reverse_lazy("detail_animal", kwargs={"pk": self.kwargs['animal_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        animal = Animal.objects.get(id=self.kwargs['animal_id'])
        context['animal'] = animal
        return context

    def form_valid(self, form):
        #Si le formulaire est valide on fait l'envoi à wordpress
        #Recuperation de l'animal concerné
        animal = Animal.objects.get(id=self.kwargs['animal_id'])
        #Etape 1 : envoi de l'image
        image = self.request.FILES['image']
        data = image.read()
        filename = image.name
        content_type = image.content_type
        user = settings.WORDPRESS_USER
        key = settings.WORDPRESS_KEY
        url = settings.WORDPRESS_URL
        creds = user + ':' + key
        token = base64.b64encode(creds.encode())
        headers = {
            'Authorization': 'Basic ' + token.decode('utf-8'),
            'Content-disposition': 'attachment; filename=%s' % filename,
            'Content-type': '%s' % content_type
        }
        r = requests.post(url + '/media', headers=headers, data=data)
        #Etape 2 : récupération des informations de l'image postée
        animal.wordpress_image_id = r.json()['id'];
        animal.wordpress_image_url= r.json()['link']
        #Etape 3 : Création de l'article
        headers = {'Authorization': 'Basic ' + token.decode('utf-8')}

        post = {'title': '%s %s' %(animal.get_type_animal_display(), animal.nom),
                'status': 'publish',
                'content': '<img src=%s"> <p> %s </p>' %(animal.wordpress_image_url,animal.get_wordpress_article()),
                'excerpt': '<img src=%s"> <p> %s </p>' %(animal.wordpress_image_url,animal.get_wordpress_article()),
                'format': 'standard',
                'categories' : '603755569'
                }
        r = requests.post(url + '/posts', headers=headers, json=post)
        #Etape 4 : récupération des informations de l'article
        animal.wordpress_id = r.json()['id'];
        animal.wordpress_url = r.json()['link']
        #Sauvegarde
        animal.save()
        return super().form_valid(form)

@login_required
def delete_wordpress(request, animal_id):
    animal = Animal.objects.get(id=animal_id)
    if request.method == "POST":
        delete_wordpress_data(animal)
        return redirect("detail_animal", pk=animal_id)

    # Render the template depending on the context.
    return render(request, "admin_interface/delete_wordpress.html", locals())

def delete_wordpress_data(animal):
    if (animal.wordpress_image_id):
        user = settings.WORDPRESS_USER
        key = settings.WORDPRESS_KEY
        url = settings.WORDPRESS_URL
        creds = user + ':' + key
        token = base64.b64encode(creds.encode())
        headers = {'Authorization': 'Basic ' + token.decode('utf-8')}
        delete = {'force': 'true'}
        # Suppression de l'article
        r = requests.delete(url + '/posts/%s' % animal.wordpress_id, headers=headers, json=delete)
        suppression_ok = r.json()['deleted']
        if suppression_ok:
            animal.wordpress_id = ""
            animal.wordpress_url = ""
        # Suppression de l'image
        r = requests.delete(url + '/media/%s' % animal.wordpress_image_id, headers=headers, json=delete)
        suppression_ok = r.json()['deleted']
        if suppression_ok:
            animal.wordpress_image_id = ""
            animal.wordpress_image_url = ""
        animal.save()