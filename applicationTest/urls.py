from django.conf.urls import url
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import CreateView
from applicationTest.models import Animal, Proprietaire
from . import views

urlpatterns = [
    url(r'^accueil/', views.home),
    url(r'^animals/$', views.search_animal, name="animals"),
    url(r'^creer_animals/$', views.create_animal.as_view(), name="creer_animal"),
    url(r'^animals/(?P<pk>\d+)$', DetailView.as_view(model=Animal,), name="detail_animal"),
    url(r'^proprietaires/$', views.search_proprietaire, name="proprietaires"),
    url(r'^creer_proprietaires/$', views.create_proprietaire.as_view(), name="creer_proprietaire"),
    url(r'^proprietaires/(?P<pk>\d+)$', DetailView.as_view(model=Proprietaire,), name="detail_proprietaire"),
]