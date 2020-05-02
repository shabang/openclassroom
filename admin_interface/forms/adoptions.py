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
        fields = ("montant", "montant_restant")
        date = DateField(
            widget=DateInput(format="%d/%m/%Y"), input_formats=("%d/%m/%Y",)
        )


class AdoptionForm(AdoptionValidator, ModelForm):
    class Meta:
        model = Adoption
        fields = ("date", "proprietaire", "montant", "montant_restant")
        date = DateField(
            widget=DateInput(format="%d/%m/%Y"), input_formats=("%d/%m/%Y",)
        )


class AdoptionFormNoProprietaire(AdoptionValidator, ModelForm):
    class Meta:
        model = Adoption
        fields = ("date", "montant", "montant_restant")

