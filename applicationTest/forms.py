from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH
from . import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.admin.widgets import AdminSplitDateTime


class DateInput(forms.DateInput):
    input_type = 'date'


class AnimalSearchForm(forms.Form):
    nom = forms.CharField(max_length=100, required=False)
    emplacement = forms.ChoiceField(choices=BLANK_CHOICE_DASH + list(models.EMPLACEMENT), widget=forms.Select(),
                                    required=False)
    type_animal = forms.ChoiceField(choices=BLANK_CHOICE_DASH + list(models.TYPE_ANIMAL), widget=forms.Select(),
                                    required=False)
    proprietaire = forms.ModelChoiceField(queryset=models.Proprietaire.objects.all(), required=False)
    date_naissance_min = forms.DateField(label="Date de naissance entre le", required=False, widget=DateInput())
    date_naissance_max = forms.DateField(label=" et le ", required=False, widget=DateInput())
    date_arrivee_min = forms.DateField(label="Date de première arrivée entre le", required=False, widget=DateInput())
    date_arrivee_max = forms.DateField(label=" et le ", required=False, widget=DateInput())
    date_prochaine_visite_min = forms.DateField(label="Date de prochaine visite vétérinaire entre le", required=False,
                                                widget=DateInput())
    date_prochaine_visite_max = forms.DateField(label=" et le ", required=False, widget=DateInput())
    date_adoption_min = forms.DateField(label="Date d'adoption entre le", required=False, widget=DateInput())
    date_adoption_max = forms.DateField(label=" et le ", required=False, widget=DateInput())


class ProprietaireSearchForm(forms.Form):
    nom = forms.CharField(max_length=100, required=False)


class SejourSearchForm(forms.Form):
    date_debut_min = forms.DateField(label="Date de début du séjour entre le", required=False, widget=DateInput())
    date_debut_max = forms.DateField(label=" et le ", required=False, widget=DateInput())
    date_fin_min = forms.DateField(label="Date de fin du séjour entre le", required=False, widget=DateInput())
    date_fin_max = forms.DateField(label=" et le ", required=False, widget=DateInput())
    proprietaire = forms.ModelChoiceField(queryset=models.Proprietaire.objects.all(), required=False)


class VisiteSearchForm(forms.Form):
    date_min = forms.DateField(label="Date de la visite médicale entre le", required=False, widget=DateInput())
    date_max = forms.DateField(label=" et le ", required=False, widget=DateInput())


class AnimalCreateForm(forms.ModelForm):
    class Meta:
        model = models.Animal
        fields = ('nom', 'type_animal', 'emplacement', 'origine', 'sexe',
                  'description', 'date_naissance', 'date_arrivee', 'sterilise',
                  'vaccine', 'date_dernier_vaccin', 'proprietaire')
        date_naissance = forms.DateField(
            widget=forms.DateInput(format='%d/%m/%Y'),
            input_formats=('%d/%m/%Y',)
        )
        date_arrivee = forms.DateField(
            widget=forms.DateInput(format='%d/%m/%Y'),
            input_formats=('%d/%m/%Y',)
        )
        date_dernier_vaccin = forms.DateField(
            widget=forms.DateInput(format='%d/%m/%Y'),
            input_formats=('%d/%m/%Y',)
        )

    # Appelé à la validation du formulaire

    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)
        emplacement = cleaned_data.get('emplacement')
        # Si l'animal est inscrit en pension, il doit avoir un proprietaire
        if emplacement == "PENSION":
            if not cleaned_data.get('proprietaire'):
                msg = "Pour un animal inscrit en pension, veuillez obligatoirement indiquer un propriétaire"
                self._errors["proprietaire"] = self.error_class([msg])
                del cleaned_data["proprietaire"]
            if cleaned_data.get('origine'):
                msg = "L'origine n'est à remplir que pour un animal du refuge."
                self._errors["origine"] = self.error_class([msg])
                del cleaned_data["origine"]
        # Si l'animal arrive au refuge, on doit indiquer sa date d'arrivée
        # Et il n'a pas de proprietaire
        elif emplacement == "REFUGE":
            if not cleaned_data.get('date_arrivee'):
                msg = "Veuillez indiquer obligatoirement la date d'arrivée de l'animal au refuge."
                self._errors["date_arrivee"] = self.error_class([msg])
                del cleaned_data["date_arrivee"]
            if not cleaned_data.get('origine'):
                msg = "Veuillez indiquer obligatoirement l'origine de l'animmal."
                self._errors["origine"] = self.error_class([msg])
                del cleaned_data["origine"]
            if cleaned_data.get('proprietaire'):
                msg = "Si l'animal arrive au refuge, il n'a pas de propriétaire."
                self._errors["proprietaire"] = self.error_class([msg])
                del cleaned_data["proprietaire"]
        # Si l'animal est vaccine, la date de dernier vaccin est obligatoire
        vaccine = cleaned_data.get('vaccine')
        if vaccine == "OUI":
            date_vaccin = cleaned_data.get('date_dernier_vaccin')
            if not date_vaccin:
                msg = "Comme l'animal est vacciné, veuillez obligatoirement indiquer la date du dernier vaccin"
                self._errors["date_dernier_vaccin"] = self.error_class([msg])
                del cleaned_data["date_dernier_vaccin"]

        return cleaned_data


class AnimalUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Animal
        fields = ('description', 'date_naissance', 'date_arrivee', 'sterilise',
                  'vaccine', 'date_dernier_vaccin')
        date_naissance = forms.DateField(
            widget=forms.DateInput(format='%d/%m/%Y'),
            input_formats=('%d/%m/%Y',)
        )
        date_arrivee = forms.DateField(
            widget=forms.DateInput(format='%d/%m/%Y'),
            input_formats=('%d/%m/%Y',)
        )
        date_dernier_vaccin = forms.DateField(
            widget=forms.DateInput(format='%d/%m/%Y'),
            input_formats=('%d/%m/%Y',)
        )

    # Appelé à la validation du formulaire
    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)
        emplacement = self.object.emplacement

        # Si l'animal arrive au refuge, on doit indiquer sa date d'arrivée
        # Et il n'a pas de proprietaire
        if emplacement == "REFUGE":
            if not cleaned_data.get('date_arrivee'):
                msg = "Veuillez indiquer obligatoirement la date d'arrivée de l'animal au refuge."
                self._errors["date_arrivee"] = self.error_class([msg])
                del cleaned_data["date_arrivee"]

        # Si l'animal est vaccine, la date de dernier vaccin est obligatoire
        vaccine = cleaned_data.get('vaccine')
        if vaccine == "OUI":
            date_vaccin = cleaned_data.get('date_dernier_vaccin')
            if not date_vaccin:
                msg = "Comme l'animal est vacciné, veuillez obligatoirement indiquer la date du dernier vaccin"
                self._errors["date_dernier_vaccin"] = self.error_class([msg])
                del cleaned_data["date_dernier_vaccin"]

        return cleaned_data


class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)


class UserForm(forms.ModelForm):
    first_name = forms.CharField(required=True, label="Prénom")
    last_name = forms.CharField(required=True, label="Nom")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProprietaireForm(forms.ModelForm):
    class Meta:
        model = models.Proprietaire
        fields = ('adresse', 'telephone')


class AdoptionForm(forms.ModelForm):
    class Meta:
        model = models.Adoption
        fields = ('date', 'proprietaire', 'montant', 'montant_restant')
        date = forms.DateField(
            widget=forms.DateInput(format='%d/%m/%Y'),
            input_formats=('%d/%m/%Y',)
        )


class AdoptionFormNoProprietaire(forms.ModelForm):
    class Meta:
        model = models.Adoption
        fields = ('date', 'montant', 'montant_restant')


class SejourForm(forms.ModelForm):
    date_arrivee = forms.SplitDateTimeField(required=True, widget=AdminSplitDateTime())
    date_depart = forms.SplitDateTimeField(required=True, widget=AdminSplitDateTime())

    class Meta:
        model = models.Sejour
        fields = ('date_arrivee', 'date_depart', 'proprietaire', 'animaux', 'nb_cages_fournies', 'nb_cages_a_fournir',
                  'vaccination', 'soin', 'injection', 'commentaire')

    # Pour gérer le lien entre le champ "propriétaire et le champ "Animaux"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['animaux'].queryset = models.Animal.objects.none()

        if 'proprietaire' in self.data:
            try:
                proprietaire_id = int(self.data.get('proprietaire'))
                self.fields['animaux'].queryset = models.Animal.objects.filter(
                    proprietaire_id=proprietaire_id).order_by('nom')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty animaux queryset

    # Appelé à la validation du formulaire
    @property
    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)
        date_arrivee = cleaned_data.get('date_arrivee')
        date_depart = cleaned_data.get('date_depart')
        # Vérification de la cohérence de la date d'arrivée et de la date de départ
        if date_arrivee and date_arrivee < timezone.now():
            msg = "La date d'arrivée ne peut être avant aujourd'hui"
            self._errors["date_arrivee"] = self.error_class([msg])
            del cleaned_data["date_arrivee"]
        if date_arrivee and date_depart and date_arrivee > date_depart:
            msg = "La date de départ ne peuse trouver avant la date d'arrivée"
            self._errors["date_depart"] = self.error_class([msg])
            del cleaned_data["date_depart"]

        return cleaned_data
