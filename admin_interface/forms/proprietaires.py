from django.forms import ModelForm, CharField, Form, DateField

from admin_interface.forms import DateInput
from admin_interface.models.proprietaires import Proprietaire, Avoir


class ProprietaireSearchForm(Form):
    nom = CharField(max_length=100, required=False)
    prenom = CharField(max_length=100, required=False)
    ville = CharField(max_length=100, required=False)
    telephone = CharField(max_length=100, required=False)

class ProprietaireDateForm(Form):
    date_adoption = DateField(
        label="Affichage des adoptions du mois précédent le", required=False, widget=DateInput()
    )


class ProprietaireForm(ModelForm):
    class Meta:
        model = Proprietaire
        fields = ("adresse","code_postal","ville", "telephone","deuxieme_telephone","inactif"
                  , "tarif_special","cadeau_recu", "commentaire")

    def clean_ville(self):
        return self.cleaned_data['ville'].upper()

class AvoirForm(ModelForm):
    class Meta:
        model = Avoir
        fields = ("date_obtention","montant", "commentaire","proprietaire")
