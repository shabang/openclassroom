from django.forms import ModelForm, CharField, Form

from admin_interface.models.proprietaires import Proprietaire, Avoir


class ProprietaireSearchForm(Form):
    nom = CharField(max_length=100, required=False)


class ProprietaireForm(ModelForm):
    class Meta:
        model = Proprietaire
        fields = ("adresse","code_postal","ville", "telephone","deuxieme_telephone","inactif"
                  , "tarif_special","cadeau_recu")

class AvoirForm(ModelForm):
    class Meta:
        model = Avoir
        fields = ("date_obtention","montant", "commentaire","proprietaire")