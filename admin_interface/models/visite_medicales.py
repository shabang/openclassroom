from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from . import OuiNonChoice, TypeVisiteVetoChoice


class VisiteMedicale(models.Model):
    date_mise_a_jour = models.DateField(
        verbose_name="Date de mise à jour", auto_now=True
    )
    date = models.DateField(verbose_name="Date de la visite")
    type_visite = models.CharField(
        max_length=30,
        verbose_name="Objet de la visite",
        choices=[(tag.name, tag.value) for tag in TypeVisiteVetoChoice],
    )
    commentaire = models.CharField(max_length=2000, blank=True)
    montant = models.DecimalField(
        verbose_name="Montant", max_digits=7, decimal_places=2, blank=True, null=True
    )
    animaux = models.ManyToManyField("Animal")

    def __str__(self):
        return f"visite {self.type_visite} le {self.date}"


@receiver(m2m_changed, sender=VisiteMedicale.animaux.through)
def visite_medicale_save_action(sender, instance, **kwargs):
    # Instance est une visite médicale
    if instance.type_visite in (
        TypeVisiteVetoChoice.STE.name,
        TypeVisiteVetoChoice.VAC.name,
    ):
        for animal in instance.animaux.all():
            if instance.type_visite == TypeVisiteVetoChoice.STE.name:
                animal.sterilise = OuiNonChoice.OUI.name
                animal.date_sterilisation = instance.date
            elif instance.type_visite == TypeVisiteVetoChoice.VAC.name:
                animal.vaccine = OuiNonChoice.OUI.name
                animal.date_dernier_vaccin = instance.date
            animal.save()
