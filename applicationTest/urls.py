from django.urls import path
from django.views.generic import DetailView
from applicationTest.models import Animal, Proprietaire, Sejour
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('accueil/', views.home, name="accueil"),
    path('animals/', views.search_animal, name="animals"),
    path('creer_animals/', login_required(views.create_animal.as_view()), name="creer_animal"),
    path('modifier_animal/<int:pk>/', login_required(views.update_animal.as_view()), name="modifier_animal"),
    path('detail_animal/<int:pk>/', login_required(DetailView.as_view(model=Animal,)), name="detail_animal"),
    path('proprietaires/', views.search_proprietaire, name="proprietaires"),
    path('creer_proprietaires/', views.create_proprietaire, name="creer_proprietaire"),
    path('modifier_proprietaire/<int:pk>/', views.update_proprietaire, name="modifier_proprietaire"),
    path('proprietaires/<int:pk>/', login_required(DetailView.as_view(model=Proprietaire,)), name="detail_proprietaire"),
    path('login/', views.connexion, name="login"),
    path('sejours/', views.search_sejour, name="sejours"),
    path('creer_sejour/', login_required(views.create_sejour.as_view()), name="creer_sejour"),
    path('detail_sejour/<int:pk>/', login_required(DetailView.as_view(model=Sejour,)), name="detail_sejour"),
    path('visites/', views.search_visite, name="visites"),
    path('creer_visite/', login_required(views.create_visite.as_view()), name="creer_visite"),
    path('ajax/load-animals/', views.load_animals, name='ajax_load_animals'),
    path('parametrage_tarifaire/', views.parametrage_tarifaire, name="parametrage_tarifaire"),
    path('animals/adoption/<int:pk>/',  views.adoption, name="adoption"),
    path('animals/adoption_complete/<int:pk>/',  views.adoption_complete, name="adoption_complete"),
    path('animals/adoption_allegee/<int:pk>/',  views.adoption_allegee, name="adoption_allegee"),
    path('animals/update_adoption/<int:pk>/',  login_required(views.update_adoption.as_view()), name="update_adoption"),
]