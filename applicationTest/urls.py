from django.conf.urls import url
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import CreateView
from applicationTest.models import Animal, Proprietaire
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^accueil/', views.home, name="accueil"),
    url(r'^animals/', views.search_animal, name="animals"),
    url(r'^creer_animals/$', login_required(views.create_animal.as_view()), name="creer_animal"),
    url(r'^animal_detail/(?P<pk>\d+)$', login_required(DetailView.as_view(model=Animal,)), name="detail_animal"),
    url(r'^proprietaires/$', views.search_proprietaire, name="proprietaires"),
    url(r'^creer_proprietaires/$', login_required(views.create_proprietaire.as_view()), name="creer_proprietaire"),
    url(r'^proprietaires/(?P<pk>\d+)$', login_required(DetailView.as_view(model=Proprietaire,)), name="detail_proprietaire"),
    url(r'^login/$', views.connexion, name="login"),
    url(r'^sejours/', views.search_sejour, name="sejours"),
    url(r'^visites/', views.search_visite, name="visites"),
]