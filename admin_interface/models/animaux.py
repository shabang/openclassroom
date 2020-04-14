from django.db import models

from . import (
    EmplacementChoice,
    OrigineChoice,
    OuiNonChoice,
    SexeChoice,
    TypeAnimalChoice,
)
from .adoptions import Adoption
from .proprietaires import Proprietaire
from .visite_medicales import VisiteMedicale


class Animal(models.Model):
    nom = models.CharField(max_length=100)
    date_naissance = models.DateField(
        verbose_name="Date de naissance", null=True, blank=True
    )
    date_arrivee = models.DateField(
        verbose_name="Date de première arrivée", null=True, blank=True
    )
    date_visite = models.DateField(
        verbose_name="Date de prochaine visite vétérinaire", null=True, blank=True
    )
    type_animal = models.CharField(
        max_length=30,
        verbose_name="Type d'animal",
        choices=[(tag.name, tag.value) for tag in TypeAnimalChoice],
    )
    emplacement = models.CharField(
        max_length=30,
        verbose_name="Emplacement",
        choices=[(tag.name, tag.value) for tag in EmplacementChoice],
    )
    origine = models.CharField(
        max_length=30,
        verbose_name="Origine (à remplir uniquement si animal du refuge)",
        choices=[(tag.name, tag.value) for tag in OrigineChoice],
        blank=True,
    )
    sexe = models.CharField(
        max_length=30,
        verbose_name="Sexe",
        choices=[(tag.name, tag.value) for tag in SexeChoice],
    )
    sterilise = models.CharField(
        max_length=30,
        verbose_name="Stérilisé",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    vaccine = models.CharField(
        max_length=30,
        verbose_name="Vacciné",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    date_dernier_vaccin = models.DateField(
        verbose_name="Date du dernier rappel de vaccin", null=True, blank=True
    )
    proprietaire = models.ForeignKey(
        Proprietaire,
        verbose_name="Propriétaire (à remplir uniquement si animal de la pension)",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    description = models.CharField(max_length=2000, blank=True)
    photo = models.ImageField(upload_to='animaux/', blank=True)

    def __str__(self):
        return self.nom

    def is_from_pension(self):
        return self.emplacement == EmplacementChoice.PENSION.name

    def is_from_refuge(self):
        return self.emplacement == EmplacementChoice.REFUGE.name

    def is_adopted_refuge(self):
        result = False
        try:
            result = self.adoption is not None
        except Adoption.DoesNotExist:
            pass
        return result

    def get_vaccin_str(self):
        if self.date_dernier_vaccin:
            return (
                str(self.get_vaccine_display())
                + " (dernier rappel le "
                + self.date_dernier_vaccin.strftime("%d/%m/%Y")
                + " )"
            )
        else:
            return self.get_vaccine_display()

    def save(self, *args, **kwargs):
        # A l'enregistrement de l'animal on met à jour sa date de
        # prochaine visite vétérinaire et ses informations de
        # vaccination
        date_rappel_vaccin = self.date_dernier_vaccin
        date_visites = (
            VisiteMedicale.objects.filter(animaux=self)
            .aggregate(models.Min("date"))
            .get("date__min")
        )
        if date_rappel_vaccin is not None:
            self.vaccine = OuiNonChoice.OUI.name
            if date_visites is not None:
                self.date_visite = (
                    date_visites
                    if date_visites < date_rappel_vaccin
                    else date_rappel_vaccin
                )
            else:
                self.date_visite = date_rappel_vaccin
        else:
            self.date_visite = date_visites
        return super().save(*args, **kwargs)
