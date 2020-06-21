from django.db import models

from . import OuiNonChoice, SexeChoice, TypeAnimalChoice, TypeSupplementChoice


class TarifJournalier(models.Model):
    type_animal = models.CharField(
        max_length=30,
        verbose_name="Type d'animal",
        choices=[(tag.name, tag.value) for tag in TypeAnimalChoice],
    )
    adopte_refuge = models.CharField(
        max_length=3,
        verbose_name="Adopté au refuge",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    supplementaire = models.CharField(
        max_length=3,
        verbose_name="Animal supplémentaire dans la même cage",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    montant_jour = models.DecimalField(
        verbose_name="Prix par jour", max_digits=7, decimal_places=2
    )
    tarif_special = models.BooleanField(default=False,
                                        verbose_name="Tarif préférentiel (ancien tarif)?")

    def __str__(self):
        return "Tarif journalier pour " + self.type_animal


class TarifAdoption(models.Model):
    type_animal = models.CharField(
        max_length=30,
        verbose_name="Type d'animal",
        choices=[(tag.name, tag.value) for tag in TypeAnimalChoice],
    )
    sexe = models.CharField(
        max_length=30,
        verbose_name="Sexe",
        choices=[(tag, tag.value) for tag in SexeChoice],
    )
    sterilise = models.CharField(
        max_length=3,
        verbose_name="Stérilisé",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    montant_adoption = models.DecimalField(
        verbose_name="Prix par jour", max_digits=7, decimal_places=2
    )

    def __str__(self):
        return "Tarif adoption pour " + self.type_animal


class ParametreTarifairePension(models.Model):
    type_supplement = models.CharField(
        max_length=50,
        verbose_name="Libellé du supplément",
        choices=[(tag.name, tag.value) for tag in TypeSupplementChoice],
    )
    supplement_journalier = models.CharField(
        max_length=3,
        verbose_name="Supplément journalier?",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    montant = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return "Supplément tarifaire pour  " + self.type_supplement
