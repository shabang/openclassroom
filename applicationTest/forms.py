from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH
from . import models
from django.contrib.auth.models import User

class DateInput(forms.DateInput):
    input_type = 'date'
    
class AnimalSearchForm(forms.Form):
    nom = forms.CharField(max_length=100, required=False)
    provenance = forms.ChoiceField(choices = BLANK_CHOICE_DASH + list(models.ORIGINE), widget=forms.Select(), required=False)
    type_animal = forms.ChoiceField(choices = BLANK_CHOICE_DASH + list(models.TYPE_ANIMAL), widget=forms.Select(), required=False)
    proprietaire = forms.ModelChoiceField(queryset = models.Proprietaire.objects.all(), required=False)
    date_naissance_min = forms.DateField(label = "Date de naissance entre le", required=False, widget=DateInput())
    date_naissance_max = forms.DateField(label = " et le ", required=False, widget=DateInput())
    date_arrivee_min = forms.DateField(label = "Date de première arrivée entre le", required=False, widget=DateInput())
    date_arrivee_max = forms.DateField(label = " et le ",required=False, widget=DateInput())
    date_prochaine_visite_min = forms.DateField(label = "Date de prochaine visite vétérinaire entre le",required=False, widget=DateInput())
    date_prochaine_visite_max = forms.DateField(label = " et le ",required=False, widget=DateInput())
    date_adoption_min = forms.DateField(label = "Date d'adoption entre le",required=False, widget=DateInput())
    date_adoption_max = forms.DateField(label = " et le ",required=False, widget=DateInput())
    
class ProprietaireSearchForm(forms.Form):
    nom = forms.CharField(max_length=100, required=False)
    
class SejourSearchForm(forms.Form):
    date_debut_min = forms.DateField(label = "Date de début du séjour entre le", required=False, widget=DateInput())
    date_debut_max = forms.DateField(label = " et le ",required=False, widget=DateInput())
    date_fin_min = forms.DateField(label = "Date de fin du séjour entre le", required=False, widget=DateInput())
    date_fin_max = forms.DateField(label = " et le ",required=False, widget=DateInput())
    proprietaire = forms.ModelChoiceField(queryset = models.Proprietaire.objects.all(), required=False)
    
class VisiteSearchForm(forms.Form):
    date_min = forms.DateField(label = "Date de la visite médicale entre le", required=False, widget=DateInput())
    date_max = forms.DateField(label = " et le ",required=False, widget=DateInput())
    
class AnimalForm(forms.ModelForm):
    class Meta:
        model = models.Animal
        fields = ('nom','type_animal', 'origine','sexe', 
                  'description', 'date_naissance', 'date_arrivee', 'sterilise', 
                   'vaccine', 'date_dernier_vaccin', 'proprietaire')
        widgets = {
            'date_naissance': DateInput(),
            'date_arrivee': DateInput(),
            'date_dernier_vaccin' : DateInput()
        }
    
    #Appelé à la validation du formulaire
    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)
        origine = cleaned_data.get('origine')
        #Si l'animal est inscrit en pension, il doit avoir un proprietaire
        if (origine == "PENSION"):
            if (not cleaned_data.get('proprietaire')):
                msg = "Pour un animal inscrit en pension, veuillez obligatoirement indiquer un propriétaire"
                self._errors["proprietaire"] = self.error_class([msg])
                del cleaned_data["proprietaire"]
        #Si l'animal arrive au refuge, on doit indiquer sa date d'arrivée
        elif (origine == "REFUGE"):
            if (not cleaned_data.get('date_arrivee')):
                msg = "Veuillez indiquer obligatoirement la date d'arrivée de l'animal au refuge."
                self._errors["date_arrivee"] = self.error_class([msg])
                del cleaned_data["date_arrivee"]
        #Si l'animal est vaccine, la date de dernier vaccin est obligatoire
        vaccine = cleaned_data.get('vaccine')
        if (vaccine == "OUI"):
            if (not cleaned_data.get('date_dernier_vaccin')):
                msg = "Comme l'animal est vacciné, veuillez obligatoirement indiquer la date du dernier vaccin"
                self._errors["date_dernier_vaccin"] = self.error_class([msg])
                del cleaned_data["date_dernier_vaccin"]
                
        return cleaned_data

class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    
class UserForm(forms.ModelForm):
    first_name = forms.CharField(required=True, label="Prénom")
    last_name = forms.CharField(required=True, label = "Nom")
    #Champs de l'objet Proprietaire
    adresse = forms.CharField()
    telephone = forms.CharField()

    class Meta:
        model = User
        fields = ('first_name','last_name', 'email')
        