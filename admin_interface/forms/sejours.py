from dal import autocomplete

from django.contrib.admin.widgets import AdminSplitDateTime
from django.db.models import BLANK_CHOICE_DASH
from django.forms import Form, DateField, ModelChoiceField, ModelForm, SplitDateTimeField, SplitDateTimeWidget, \
    ChoiceField, Select
from django.utils import timezone

from admin_interface.forms import DateInput
from admin_interface.models import OuiNonChoice
from admin_interface.models.animaux import Animal
from admin_interface.models.proprietaires import Proprietaire
from admin_interface.models.sejours import Sejour


class SejourSearchForm(Form):
    date_debut_min = DateField(
        label="Date de début du séjour entre le", required=False, widget=DateInput()
    )
    date_debut_max = DateField(
        label=" et le ", required=False, widget=DateInput()
    )
    date_fin_min = DateField(
        label="Date de fin du séjour entre le", required=False, widget=DateInput()
    )
    date_fin_max = DateField(label=" et le ", required=False, widget=DateInput())
    proprietaire = ModelChoiceField(
        queryset=Proprietaire.objects.all().filter(inactif=False), required=False
    )
    cohabitation = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
    )


class SejourFormBase:
    # Pour gérer le lien entre le champ "propriétaire et le champ "Animaux"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["animaux"].queryset = Animal.objects.none()
        self.fields["proprietaire"].queryset = Proprietaire.objects.all().filter(inactif=False).\
            order_by("user__last_name")

        if "proprietaire" in self.data:
            try:
                proprietaire_id = int(self.data.get("proprietaire"))
                self.fields["animaux"].queryset = Animal.objects.filter(
                    proprietaire_id=proprietaire_id
                ).filter(inactif=False).order_by("nom")
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty animaux queryset

    # Appelé à la validation du formulaire
    def clean(self):
        cleaned_data = {**super().clean()}
        if self.instance.pk is None:
            date_arrivee = cleaned_data.get("date_arrivee")
            date_depart = cleaned_data.get("date_depart")
            # Vérification de la cohérence de la date d'arrivée et de la date de départ
            if date_arrivee and date_depart and date_arrivee > date_depart:
                msg = "La date de départ ne peuse trouver avant la date d'arrivée"
                self._errors["date_depart"] = self.error_class([msg])
                del cleaned_data["date_depart"]

        return cleaned_data


class SejourForm(SejourFormBase, ModelForm):
    date_arrivee = SplitDateTimeField(required=True, widget=SplitDateTimeWidget(time_format=('%H:%M')))
    date_depart = SplitDateTimeField(required=True, widget=SplitDateTimeWidget(time_format=('%H:%M')))

    class Meta:
        model = Sejour
        fields = (
            "cohabitation",
            "date_arrivee",
            "date_depart",
            "proprietaire",
            "animaux",
            "nb_cages_fournies",
            "nb_cages_a_fournir",
            "vaccination",
            "soin",
            "injection",
            "commentaire",
            "montant",
            "arrhes",
            "montant_restant",
        )
        widgets = {
            'proprietaire': autocomplete.ModelSelect2(url='proprietaire_autocomplete')
        }

class SejourStatsForm(Form):
    date_debut = DateField(
        label="Affichage des séjours à partir du", required=False, widget=DateInput()
    )

class SejourGainForm(Form):
    date_debut_gain = DateField(
        label="Rechercher le montant des pensions entre le ", required=False, widget=DateInput())
    date_fin_gain = DateField(
        label="et le ", required=False, widget=DateInput()
    )