from django.forms import ModelForm, CharField, Form

from admin_interface.models.proprietaires import Proprietaire


class ProprietaireSearchForm(Form):
    nom = CharField(max_length=100, required=False)


class ProprietaireForm(ModelForm):
    class Meta:
        model = Proprietaire
        fields = ("adresse","code_postal","ville", "telephone","deuxieme_telephone","inactif", "tarif_special")
