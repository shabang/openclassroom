from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import DetailView

from admin_interface.models.animaux import Animal
from admin_interface.models.proprietaires import Proprietaire
from admin_interface.models.sejours import Sejour
from admin_interface.models.visite_medicales import VisiteMedicale

from .views import (
    adoptions,
    animaux,
    home,
    proprietaires,
    sejours,
    tarifs,
    visite_medicales,
)

urlpatterns = [
    path('', home.index, name="accueil"),

    # Animaux
    path('animals/', animaux.search_animal, name="animals"),
    path('animals/create', animaux.CreateAnimal.as_view(), name="creer_animal"),
    path('animals/update/<int:pk>/', animaux.UpdateAnimal.as_view(), name="modifier_animal"),
    path('animals/<int:pk>/', login_required(DetailView.as_view(model=Animal)), name="detail_animal"),
    path('ajax/load-animals/', animaux.load_animals, name='ajax_load_animals'),

    # Proprietaires
    path('proprietaires/', proprietaires.search_proprietaire, name="proprietaires"),
    path('proprietaires/create', proprietaires.create_proprietaire, name="creer_proprietaire"),
    path('proprietaires/update//<int:pk>/', proprietaires.update_proprietaire, name="modifier_proprietaire"),
    path('proprietaires/<int:pk>/', login_required(DetailView.as_view(model=Proprietaire)), name="detail_proprietaire"),

    # Séjours
    path('sejours/', sejours.search_sejour, name="sejours"),
    path('sejours/create', sejours.CreateSejour.as_view(), name="creer_sejour"),
    path('sejours/update/<int:pk>/', sejours.UpdateSejour.as_view(), name="modifier_sejour"),
    path('sejours/<int:pk>/', login_required(DetailView.as_view(model=Sejour)), name="detail_sejour"),
    path('ajax/calcul_montant/', sejours.calcul_montant_sejour, name="calcul_montant_sejour"),

    # Visites médicales
    path('visites/', visite_medicales.search_visite, name="visites"),
    path('visites/create/',visite_medicales.CreateVisite.as_view(), name="creer_visite"),
    path('visites/update/<int:pk>/',visite_medicales.UpdateVisite.as_view(), name="update_visite"),
    path('visites/<int:pk>/', login_required(DetailView.as_view(model=VisiteMedicale)), name="detail_visite"),

    # Tarifs
    path('parametrage_tarifaire/', tarifs.parametrage_tarifaire, name="parametrage_tarifaire"),

    # Adoptions
    path('animals/adoption/<int:pk>/',  adoptions.index, name="adoption"),
    path('animals/adoption_complete/<int:pk>/',  adoptions.adoption_complete, name="adoption_complete"),
    path('animals/adoption_allegee/<int:pk>/',  adoptions.adoption_allegee, name="adoption_allegee"),
    path('animals/update_adoption/<int:pk>/', adoptions.UpdateAdoption.as_view(), name="update_adoption"),
]
