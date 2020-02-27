#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import CreateView
from applicationTest.forms import AnimalSearchForm, ProprietaireSearchForm, AnimalForm, ConnexionForm
from applicationTest.models import Animal, Proprietaire, VisiteMedicale, Sejour, ORIGINE,\
    Adoption
from django.urls import reverse_lazy
from _datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import authenticate, login

def connexion(request):
    error = False
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username = username, password = password)
            if user :
                login(request, user)
            else:
                error = True
    else:
        form = ConnexionForm()
    return render(request, 'applicationTest/login.html', locals())
    
    
    
@login_required
def home(request):
    
    # Pour la sidebar
    selected = "tableau_bord"
    
    # Dates
    today = timezone.now()
    interval = timezone.now() + timedelta(days = 7)
    # Partie pension
    arrivees_pension = Sejour.objects.filter(date_arrivee__gt = today).filter(date_arrivee__lt = interval).count()
    departs_pension = Sejour.objects.filter(date_depart__gt = today).filter(date_depart__lt = interval).count()
    presences = Sejour.objects.filter(date_arrivee__lt = today).filter(date_depart__gt = today).count()
    # Partie refuge
    rdv_veterinaire = VisiteMedicale.objects.filter(date__gt=today).filter(date__lt= interval).count()
    recuperations = Animal.objects.filter(origine = "REFUGE").filter(date_arrivee__gt = today).filter(date_arrivee__lt = interval).count()
    adoptions = Adoption.objects.filter(date__gt=today).filter(date__lt= interval).count()
    
    return render(request, 'applicationTest/tableau_bord.html', locals())

class create_animal(CreateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'applicationTest/animal_form.html'
    success_url = reverse_lazy('animals')
    
    def get_context_data(self, **kwargs):
        context = CreateView.get_context_data(self, **kwargs)
        context['selected'] = "create_animal" 
        return context
    
class create_proprietaire(CreateView):
    model = Proprietaire
    template_name = 'applicationTest/proprietaire_form.html'
    fields = ('nom','prenom','mail','adresse', 'telephone')
    success_url = reverse_lazy('proprietaires')
    
    def get_context_data(self, **kwargs):  
        context = CreateView.get_context_data(self, **kwargs)
        context['selected'] = "create_proprietaire" 
        return context 
    
class create_visite(CreateView):
    model = VisiteMedicale
    template_name = 'applicationTest/visite_form.html'
    fields = ('date','type_visite','commentaire')
    success_url = reverse_lazy('animals')

class create_sejour(CreateView):
    model = Sejour
    template_name = 'applicationTest/sejour_form.html'
    fields = ('date_arrivee','date_depart','cage','montant')
    success_url = reverse_lazy('animals')      
  
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
            date_naissance_min = form.cleaned_data['date_naissance_min']
            date_naissance_max = form.cleaned_data['date_naissance_max']
            date_arrivee_min = form.cleaned_data['date_arrivee_min']
            date_arrivee_max = form.cleaned_data['date_arrivee_max']
            date_prochaine_visite_min = form.cleaned_data['date_prochaine_visite_min']
            date_prochaine_visite_max =form.cleaned_data['date_prochaine_visite_max']
            
            if (proprietaire_form != None):
                animals = animals.filter(proprietaire=proprietaire_form)
            if(type_animal_form):
                animals = animals.filter(type_animal = type_animal_form)
            if(nom_form != None):
                animals = animals.filter(nom__icontains = nom_form)
            if (date_naissance_min):
                animals = animals.filter(date_naissance__gte = date_naissance_min)
            if (date_naissance_max):
                animals = animals.filter(date_naissance__lte = date_naissance_max)
            if (date_arrivee_min):
                animals = animals.filter(date_arrivee__gte = date_arrivee_min)
            if (date_arrivee_max):
                animals = animals.filter(date_arrivee__lte = date_arrivee_max)
            if (date_prochaine_visite_min):
                animals = animals.filter(date_prochaine_visite__gte = date_prochaine_visite_min)
            if (date_prochaine_visite_max):
                animals = animals.filter(date_prochaine_visite__lte = date_prochaine_visite_max)
    else:
        form = AnimalSearchForm()
    return render(request, 'applicationTest/animal_list.html', locals())

@login_required    
def search_proprietaire(request):
    
    selected = "proprietaires"
    proprietaires = Proprietaire.objects.all()
    
    if request.method == 'POST':
        form = ProprietaireSearchForm(request.POST)
        if form.is_valid():
        
            nom_form = form.cleaned_data['nom']

            if(nom_form != None):
                proprietaires = proprietaires.filter(nom__icontains = nom_form)
    else:
        form = ProprietaireSearchForm()
    return render(request, 'applicationTest/proprietaire_list.html', locals())