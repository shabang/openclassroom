from django.urls import path
from django.views.generic import DetailView
from admin_interface.models import Animal, Proprietaire, Sejour, VisiteMedicale
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('accueil/', views.home, name="accueil"),
    path('animals/', views.search_animal, name="animals"),
    path('creer_animals/', views.CreateAnimal.as_view(), name="creer_animal"),
    path('modifier_animal/<int:pk>/', views.UpdateAnimal.as_view(), name="modifier_animal"),
    path('detail_animal/<int:pk>/', login_required(DetailView.as_view(model=Animal,)), name="detail_animal"),
    path('proprietaires/', views.search_proprietaire, name="proprietaires"),
    path('creer_proprietaires/', views.create_proprietaire, name="creer_proprietaire"),
    path('modifier_proprietaire/<int:pk>/', views.update_proprietaire, name="modifier_proprietaire"),
    path('proprietaires/<int:pk>/', login_required(DetailView.as_view(model=Proprietaire,)), name="detail_proprietaire"),
    path('login/', views.connexion, name="login"),
    path('sejours/', views.search_sejour, name="sejours"),
    path('creer_sejour/', views.CreateSejour.as_view(), name="creer_sejour"),
    path('modifier_sejour/<int:pk>/', views.UpdateSejour.as_view(), name="modifier_sejour"),
    path('detail_sejour/<int:pk>/', login_required(DetailView.as_view(model=Sejour,)), name="detail_sejour"),
    path('visites/', views.search_visite, name="visites"),
    path('creer_visite/',views.CreateVisite.as_view(), name="creer_visite"),
    path('update_visite/<int:pk>/',views.UpdateVisite.as_view(), name="update_visite"),
    path('detail_visite/<int:pk>/', login_required(DetailView.as_view(model=VisiteMedicale,)), name="detail_visite"),
    path('ajax/load-animals/', views.load_animals, name='ajax_load_animals'),
    path('parametrage_tarifaire/', views.parametrage_tarifaire, name="parametrage_tarifaire"),
    path('animals/adoption/<int:pk>/',  views.adoption, name="adoption"),
    path('animals/adoption_complete/<int:pk>/',  views.adoption_complete, name="adoption_complete"),
    path('animals/adoption_allegee/<int:pk>/',  views.adoption_allegee, name="adoption_allegee"),
    path('animals/update_adoption/<int:pk>/', views.UpdateAdoption.as_view(), name="update_adoption"),
    path('ajax/calcul_montant/', views.calcul_montant_sejour, name="calcul_montant_sejour"),
]
