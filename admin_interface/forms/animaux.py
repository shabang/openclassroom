from django.db.models import BLANK_CHOICE_DASH
from django.forms import DateField, Form, CharField, ChoiceField, Select, ModelChoiceField, ModelForm, FileInput

from admin_interface.forms import DateInput
from admin_interface.models import EmplacementChoice, TypeAnimalChoice, OuiNonChoice
from admin_interface.models.animaux import Animal
from admin_interface.models.proprietaires import Proprietaire


class AnimalSearchForm(Form):
    nom = CharField(max_length=100, required=False)
    emplacement = ChoiceField(
        choices=BLANK_CHOICE_DASH
                + [(tag.name, tag.value) for tag in EmplacementChoice],
        widget=Select(),
        required=False,
    )
    type_animal = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in TypeAnimalChoice],
        widget=Select(),
        required=False,
    )
    proprietaire = ModelChoiceField(
        queryset=Proprietaire.objects.all(), required=False
    )
    date_naissance_min = DateField(
        label="Date de naissance entre le", required=False, widget=DateInput()
    )
    date_naissance_max = DateField(
        label=" et le ", required=False, widget=DateInput()
    )
    date_arrivee_min = DateField(
        label="Date de première arrivée entre le", required=False, widget=DateInput()
    )
    date_arrivee_max = DateField(
        label=" et le ", required=False, widget=DateInput()
    )
    date_prochaine_visite_min = DateField(
        label="Date de prochaine visite vétérinaire entre le",
        required=False,
        widget=DateInput(),
    )
    date_prochaine_visite_max = DateField(
        label=" et le ", required=False, widget=DateInput()
    )
    date_adoption_min = DateField(
        label="Date d'adoption entre le", required=False, widget=DateInput()
    )
    date_adoption_max = DateField(
        label=" et le ", required=False, widget=DateInput()
    )


class AnimalValidator:
    def clean(self):
        cleaned_data = {**super().clean()}

        vaccine = cleaned_data.get("vaccine")
        if vaccine == OuiNonChoice.OUI.name:
            date_vaccin = cleaned_data.get("date_dernier_vaccin")
            if not date_vaccin:
                msg = (
                    "Comme l'animal est vacciné, veuillez obligatoirement "
                    "indiquer la date du dernier vaccin"
                )
                self._errors["date_dernier_vaccin"] = self.error_class([msg])
                del cleaned_data["date_dernier_vaccin"]

        return cleaned_data


class AnimalCreateForm(AnimalValidator, ModelForm):
    class Meta:
        model = Animal
        fields = (
            "nom",
            "type_animal",
            "emplacement",
            "origine",
            "sexe",
            "description",
            "sante",
            "date_naissance",
            "date_arrivee",
            "sterilise",
            "vaccine",
            "date_dernier_vaccin",
            "proprietaire",
            "photo",
        )
        date_naissance = DateField(
            widget=DateInput(format="%d/%m/%Y"), input_formats=("%d/%m/%Y",)
        )
        date_arrivee = DateField(
            widget=DateInput(format="%d/%m/%Y"), input_formats=("%d/%m/%Y",)
        )
        date_dernier_vaccin = DateField(
            widget=DateInput(format="%d/%m/%Y"), input_formats=("%d/%m/%Y",)
        )
        # Appelé à la validation du formulaire

        def clean(self):
            cleaned_data = {**super().clean()}
            emplacement = cleaned_data.get("emplacement")
            # Si l'animal est inscrit en pension, il doit avoir un proprietaire
            if emplacement == EmplacementChoice.PENSION.name:
                if not cleaned_data.get("proprietaire"):
                    msg = "Pour un animal inscrit en pension, veuillez obligatoirement indiquer un propriétaire"
                    self._errors["proprietaire"] = self.error_class([msg])
                    del cleaned_data["proprietaire"]
                if cleaned_data.get("origine"):
                    msg = "L'origine n'est à remplir que pour un animal du refuge."
                    self._errors["origine"] = self.error_class([msg])
                    del cleaned_data["origine"]
            # Si l'animal arrive au refuge, on doit indiquer sa date d'arrivée
            # Et il n'a pas de proprietaire
            elif emplacement == EmplacementChoice.REFUGE.name:
                if not cleaned_data.get("date_arrivee"):
                    msg = "Veuillez indiquer obligatoirement la date d'arrivée de l'animal au refuge."
                    self._errors["date_arrivee"] = self.error_class([msg])
                    del cleaned_data["date_arrivee"]
                if not cleaned_data.get("origine"):
                    msg = "Veuillez indiquer obligatoirement l'origine de l'animmal."
                    self._errors["origine"] = self.error_class([msg])
                    del cleaned_data["origine"]
                if cleaned_data.get("proprietaire"):
                    msg = "Si l'animal arrive au refuge, il n'a pas de propriétaire."
                    self._errors["proprietaire"] = self.error_class([msg])
                    del cleaned_data["proprietaire"]

            return cleaned_data


class AnimalUpdateForm(AnimalValidator, ModelForm):
    class Meta:
        model = Animal
        fields = (
            "description",
            "sante",
            "date_naissance",
            "date_arrivee",
            "sterilise",
            "vaccine",
            "date_dernier_vaccin",
            "photo",
        )
        date_naissance = DateField(
            widget=DateInput(format="%d/%m/%Y"), input_formats=("%d/%m/%Y",)
        )
        date_arrivee = DateField(
            widget=DateInput(format="%d/%m/%Y"), input_formats=("%d/%m/%Y",)
        )
        date_dernier_vaccin = DateField(
            widget=DateInput(format="%d/%m/%Y"), input_formats=("%d/%m/%Y",)
        )

    # Appelé à la validation du formulaire
    def clean(self):
        cleaned_data = ModelForm.clean(self)
        emplacement = self.instance.emplacement

        # Si l'animal arrive au refuge, on doit indiquer sa date d'arrivée
        # Et il n'a pas de proprietaire
        if emplacement == EmplacementChoice.REFUGE.name:
            if not cleaned_data.get("date_arrivee"):
                msg = "Veuillez indiquer obligatoirement la date d'arrivée de l'animal au refuge."
                self._errors["date_arrivee"] = self.error_class([msg])
                del cleaned_data["date_arrivee"]

        return cleaned_data
