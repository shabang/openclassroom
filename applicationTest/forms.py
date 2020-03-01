from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH
from . import models

class DateInput(forms.DateInput):
    input_type = 'date'
    
class AnimalSearchForm(forms.Form):
    nom = forms.CharField(max_length=100, required=False)
    provenance = forms.ChoiceField(choices = BLANK_CHOICE_DASH + list(models.ORIGINE), widget=forms.Select(), required=False)
    type_animal = forms.ChoiceField(choices = BLANK_CHOICE_DASH + list(models.TYPE_ANIMAL), widget=forms.Select(), required=False)
    proprietaire = forms.ModelChoiceField(queryset = models.Proprietaire.objects.all(), required=False)
    date_naissance_min = forms.DateField(required=False, widget=DateInput())
    date_naissance_max = forms.DateField(required=False, widget=DateInput())
    date_arrivee_min = forms.DateField(required=False, widget=DateInput())
    date_arrivee_max = forms.DateField(required=False, widget=DateInput())
    date_prochaine_visite_min = forms.DateField(required=False, widget=DateInput())
    date_prochaine_visite_max = forms.DateField(required=False, widget=DateInput())
    
class ProprietaireSearchForm(forms.Form):
    nom = forms.CharField(max_length=100, required=False)
    
class AnimalForm(forms.ModelForm):
    class Meta:
        model = models.Animal
        fields = ('nom','type_animal','sexe', 'description', 'date_naissance', 'date_arrivee', 'sterilise', 'origine', 'vaccine', 'proprietaire')
        widgets = {
            'date_naissance': DateInput(),
            'date_arrivee': DateInput()
        }

class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)