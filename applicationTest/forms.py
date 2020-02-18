from django import forms
from . import models

class AnimalSearchForm(forms.Form):
    nom = forms.CharField(max_length=100, required=False)
    provenance = forms.ChoiceField(choices = models.ORIGINE, initial='', widget=forms.Select(), required=False)
    type_animal = forms.ChoiceField(choices = models.TYPE_DEMANDE, initial='', widget=forms.Select(), required=False)
    proprietaire = forms.ModelChoiceField(queryset = models.Proprietaire.objects.all(), required=False)
    date_naissance_min = forms.DateField(required=False, widget=forms.SelectDateWidget())
    date_naissance_max = forms.DateField(required=False, widget=forms.SelectDateWidget())
    date_arrivee_min = forms.DateField(required=False, widget=forms.SelectDateWidget())
    date_arrivee_max = forms.DateField(required=False, widget=forms.SelectDateWidget())
    date_prochaine_visite_min = forms.DateField(required=False, widget=forms.SelectDateWidget())
    date_prochaine_visite_max = forms.DateField(required=False, widget=forms.SelectDateWidget())
    
class ProprietaireSearchForm(forms.Form):
    nom = forms.CharField(max_length=100, required=False)
    