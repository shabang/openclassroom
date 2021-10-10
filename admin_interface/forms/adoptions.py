from dal import autocomplete
from django.forms import ModelForm, DateField, DateInput

from admin_interface.models.adoptions import Adoption


class AdoptionValidator:
    def clean(self):
        cleaned_data = {**super().clean()}

        # Le montant restant ne peut être supérieur au montant total
        montant = cleaned_data.get("montant")
        montant_restant = cleaned_data.get("montant_restant")
        if montant_restant and montant < montant_restant:
            msg = "Le montant restant ne peut-être supérieur au montant total."
            self._errors["montant_restant"] = self.error_class([msg])
            del cleaned_data["montant_restant"]

        return cleaned_data


class AdoptionUpdateForm(AdoptionValidator, ModelForm):
    class Meta:
        model = Adoption
        fields = ("date","montant", "montant_restant",
                  "montant_caution_sterilisation", "date_caution_sterilisation",
                  "montant_caution_vaccination", "date_caution_vaccination",
                  "montant_caution_materiel", "date_caution_materiel","date_rappel_caution")
        date = DateField(
            widget=DateInput(format="%d/%m/%Y"), input_formats=("%d/%m/%Y",)
        )


class AdoptionForm(AdoptionValidator, ModelForm):
    class Meta:
        model = Adoption
        fields = ("date", "proprietaire", "montant", "montant_restant",
                  "montant_caution_sterilisation", "date_caution_sterilisation",
                  "montant_caution_vaccination", "date_caution_vaccination",
                  "montant_caution_materiel", "date_caution_materiel")
        date = DateField(
            widget=DateInput(format="%d/%m/%Y"), input_formats=("%d/%m/%Y",)
        )
        widgets = {
            'proprietaire': autocomplete.ModelSelect2(url='proprietaire_autocomplete')
        }


class AdoptionFormNoProprietaire(AdoptionValidator, ModelForm):
    class Meta:
        model = Adoption
        fields = ("date", "montant", "montant_restant",
                  "montant_caution_sterilisation", "date_caution_sterilisation",
                  "montant_caution_vaccination", "date_caution_vaccination",
                  "montant_caution_materiel", "date_caution_materiel")

