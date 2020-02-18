#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import CreateView
from django.http import HttpResponse
from datetime import datetime
from applicationTest.forms import AnimalSearchForm, ProprietaireSearchForm
from applicationTest.models import Animal, Proprietaire, VisiteMedicale, Sejour
from django.urls import reverse_lazy

def home(request):
    text = """<h1> Bienvenue sur mon blog !</h1>"""
    return HttpResponse(text)

class create_animal(CreateView):
    model = Animal
    template_name = 'applicationTest/animal_form.html'
    fields = ('nom','date_naissance','type_animal','sexe', 'description', 'date_naissance', 'date_arrivee', 'sterilise', 'origine', 'vaccine', 'proprietaire')
    success_url = reverse_lazy('animals')  
    
class create_proprietaire(CreateView):
    model = Proprietaire
    template_name = 'applicationTest/proprietaire_form.html'
    fields = ('nom','prenom','mail','adresse', 'telephone')
    success_url = reverse_lazy('proprietaires') 
    
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
  
    
def search_animal(request):
    animals = Animal.objects.all()
    if request.method == 'POST':
        form = AnimalSearchForm(request.POST)
        if form.is_valid():
        
            proprietaire_form = form.cleaned_data['proprietaire']
            type_animal_form = form.cleaned_data['type_animal']
            nom_form = form.cleaned_data['nom']
            
            if (proprietaire_form != None):
                animals = animals.filter(proprietaire=proprietaire_form)
            if(type_animal_form):
                animals = animals.filter(type_animal = type_animal_form)
            if(nom_form != None):
                animals = animals.filter(nom__icontains = nom_form)
    else:
        form = AnimalSearchForm()
    return render(request, 'applicationTest/animal_list.html', locals())
    
def search_proprietaire(request):
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