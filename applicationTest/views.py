#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView
from applicationTest.forms import AnimalSearchForm, ProprietaireSearchForm, AnimalForm, ConnexionForm, VisiteSearchForm, SejourSearchForm, UserForm, ProprietaireForm, SejourForm
from applicationTest.models import Animal, Proprietaire, VisiteMedicale, Sejour,\
    Adoption, TarifJournalier, TarifAdoption, ParametreTarifairePension
from django.urls import reverse_lazy
from _datetime import timedelta
from django.contrib.auth.decorators import login_required,permission_required
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.utils.dateparse import parse_date
from django.views.generic.detail import DetailView

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
    interval = timezone.now() + timedelta(days = 7)
    interval_str = interval.strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    # Partie pension
    arrivees_pension = Sejour.objects.filter(date_arrivee__gt = today).filter(date_arrivee__lt = interval).count()
    departs_pension = Sejour.objects.filter(date_depart__gt = today).filter(date_depart__lt = interval).count()
    presences = Sejour.objects.filter(date_arrivee__lt = today).filter(date_depart__gt = today).count()
    # Partie refuge
    rdv_veterinaire = Animal.objects.filter(origine = "REFUGE").filter(date_visite__gt=today).filter(date_visite__lt= interval).count()
    recuperations = Animal.objects.filter(origine = "REFUGE").filter(date_arrivee__gt = today).filter(date_arrivee__lt = interval).count()
    adoptions = Adoption.objects.filter(date__gt=today).filter(date__lt= interval).count()
    
    return render(request, 'applicationTest/tableau_bord.html', locals())

class create_animal(CreateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'applicationTest/animal_form.html'
    success_url = reverse_lazy('animals')
    
    def get_form(self, form_class=None):
        form = CreateView.get_form(self, form_class=form_class)
        idProprietaire = self.request.GET.get('proprietaire','')
        if (idProprietaire):
            proprietaire = Proprietaire.objects.get(id=idProprietaire)
            form.fields['proprietaire'].initial = proprietaire
        return form
    
    
class update_animal(UpdateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'applicationTest/animal_form.html'
    
    def get_success_url(self):
        return reverse_lazy('detail_animal', kwargs={'pk' : self.object.id})

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
            print (user_form.errors + proprietaire_form.errors)
    
    else:
        user_form = UserForm()
        proprietaire_form = ProprietaireForm()
    # Render the template depending on the context.
    return render(request, 'applicationTest/proprietaire_form.html', locals())

@login_required        
def update_proprietaire(request, pk):
    proprietaire_to_update = Proprietaire.objects.get(id = pk)
    
    if request.method == 'POST':
        user_form = UserForm(data=request.POST, instance = proprietaire_to_update.user)
        proprietaire_form = ProprietaireForm(data=request.POST, instance = proprietaire_to_update)
        if user_form.is_valid() and proprietaire_form.is_valid():
            user = user_form.save()
            proprietaire = proprietaire_form.save()
            return redirect('detail_proprietaire', pk=pk)
    
    else:
        user_form = UserForm(instance = proprietaire_to_update.user)
        proprietaire_form = ProprietaireForm(instance = proprietaire_to_update)
    # Render the template depending on the context.
    return render(request, 'applicationTest/proprietaire_form.html', locals())
    
    
class create_visite(CreateView):
    model = VisiteMedicale
    template_name = 'applicationTest/visite_form.html'
    fields = ('date','type_visite','montant','animaux','commentaire')
    success_url = reverse_lazy('visites')
    
    def get_form(self, form_class=None):
        form = CreateView.get_form(self, form_class=form_class)
        form.fields['animaux'].queryset = Animal.objects.filter(origine = "REFUGE")
        return form

class create_sejour(CreateView):
    model = Sejour
    template_name = 'applicationTest/sejour_form.html'
    form_class = SejourForm
    success_url = reverse_lazy('sejours')     
    def get_form(self, form_class=None):
        form = CreateView.get_form(self, form_class=form_class)
        idProprietaire = self.request.GET.get('proprietaire','')
        if (idProprietaire):
            proprietaire = Proprietaire.objects.get(id=idProprietaire)
            form.fields['proprietaire'].initial = proprietaire
            form.fields['animaux'].queryset = Animal.objects.filter(proprietaire_id=idProprietaire).order_by('nom')
        return form 
  
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
            provenance_form = form.cleaned_data['provenance']
            date_naissance_min = form.cleaned_data['date_naissance_min']
            date_naissance_max = form.cleaned_data['date_naissance_max']
            date_arrivee_min = form.cleaned_data['date_arrivee_min']
            date_arrivee_max = form.cleaned_data['date_arrivee_max']
            date_prochaine_visite_min = form.cleaned_data['date_prochaine_visite_min']
            date_prochaine_visite_max =form.cleaned_data['date_prochaine_visite_max']
            date_adoption_min = form.cleaned_data['date_adoption_min']
            date_adoption_max =form.cleaned_data['date_adoption_max']
            
            if (proprietaire_form != None):
                animals = animals.filter(proprietaire=proprietaire_form)
            if(provenance_form):
                animals = animals.filter(origine = provenance_form)
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
                animals = animals.filter(date_visite__gte = date_prochaine_visite_min)
            if (date_prochaine_visite_max):
                animals = animals.filter(date_visite__lte = date_prochaine_visite_max)
    else:
        form = AnimalSearchForm() 
        #Paramètres de l'url pour filtres par défaut
        interval_str = request.GET.get('interval','')
        filter_data = request.GET.get('filter','')
        if (filter_data):
            
            interval = parse_date(interval_str)
            today = timezone.now()
            today_str = today.strftime('%Y-%m-%d')
        
            if (filter_data == "date_visite"):
                form.fields['date_prochaine_visite_max'].initial = interval_str
                form.fields['date_prochaine_visite_min'].initial = today_str
                animals = animals.filter(date_visite__gte = today)
                animals = animals.filter(date_visite__lte = interval)
            if (filter_data == "date_arrivee"):
                form.fields['date_arrivee_max'].initial = interval_str
                form.fields['date_arrivee_min'].initial = today_str
                animals = animals.filter(date_arrivee__gte = today)
                animals = animals.filter(date_arrivee__lte = interval)
            if (filter_data == "date_adoption"):
                form.fields['date_adoption_max'].initial = interval_str
                form.fields['date_adoption_min'].initial = today_str
                animals = animals.filter(adoption__date__gte = today)
                animals = animals.filter(adoption__date__lte = interval)
            if (filter_data == "pension"):
                form.fields['provenance'].initial = "PENSION"
                animals = animals.filter(origine = "PENSION")
            if (filter_data == "refuge"):
                form.fields['provenance'].initial = "REFUGE"
                animals = animals.filter(origine = "REFUGE")
                
            
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

@login_required    
def search_visite(request):
    selected = "visites"
    visites = VisiteMedicale.objects.all()
    
    if request.method == 'POST':
        form = VisiteSearchForm(request.POST)
        if form.is_valid():
        
            date_min_form = form.cleaned_data['date_min']
            date_max_form = form.cleaned_data['date_max']

            if(date_min_form):
                visites = visites.filter(date__gte = date_min_form)
            if(date_max_form):
                visites = visites.filter(date__lte = date_max_form)
                
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

            if(date_debut_min_form):
                sejours = sejours.filter(date_arrivee__gte = date_debut_min_form)
            if(date_debut_max_form):
                sejours = sejours.filter(date_arrivee__lte = date_debut_max_form)
            if(date_fin_min_form):
                sejours = sejours.filter(date_depart__gte = date_fin_min_form)
            if(date_fin_max_form):
                sejours = sejours.filter(date_depart__lte = date_fin_max_form)
            if (proprietaire_form != None):
                sejours = sejours.filter(proprietaire=proprietaire_form)
    else:
        form = SejourSearchForm()
        
        #Paramètres de l'url pour filtres par défaut
        interval_str = request.GET.get('interval','')
        filter_data = request.GET.get('filter','')
        if (filter):
            
            interval = parse_date(interval_str)
            today = timezone.now()
            today_str = today.strftime('%Y-%m-%d')
            
            if (filter_data == "date_debut_sejour"):
                form.fields['date_debut_max'].initial = interval_str
                form.fields['date_debut_min'].initial = today_str
                sejours = sejours.filter(date_arrivee__gte = today)
                sejours = sejours.filter(date_arrivee__lte = interval)
            if (filter_data == "date_fin_sejour"):
                form.fields['date_fin_max'].initial = interval_str
                form.fields['date_fin_min'].initial = today_str
                sejours = sejours.filter(date_depart__gte = today)
                sejours = sejours.filter(date_depart__lte = interval)
            if (filter_data == "date_sejour"):
                form.fields['date_fin_min'].initial = interval_str
                form.fields['date_debut_max'].initial = today_str
                sejours = sejours.filter(date_depart__gte = interval)
                sejours = sejours.filter(date_arrivee__lte = today)
                
    return render(request, 'applicationTest/sejour_list.html', locals())

@login_required
def load_animals(request):
    proprietaire_id = request.GET.get('proprietaire')
    animaux = Animal.objects.filter(proprietaire_id=proprietaire_id)
    return render(request,'applicationTest/sejour_form_select_animals.html', {'animaux':animaux})

@login_required    
def parametrage_tarifaire(request):
    selected = "parametrage_tarifaire"
    tarifsJournaliersPension = TarifJournalier.objects.all()
    tarifsSupplements = ParametreTarifairePension.objects.all()
    tarifsAdoption = TarifAdoption.objects.all()
    return render(request,'applicationTest/parametrage_tarifaire.html', locals())
    