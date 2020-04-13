from django.db import models

from .animaux import Animal
from .proprietaires import Proprietaire


class Adoption(models.Model):
    date = models.DateField(verbose_name="Date de l'adoption")
    montant = models.DecimalField(verbose_name="Montant à payer", max_digits=7, decimal_places=2)
    montant_restant = models.DecimalField(verbose_name="Montant restant à payer", max_digits=7, decimal_places=2,
                                          null=True, blank=True)
    proprietaire = models.ForeignKey(Proprietaire, on_delete=models.PROTECT)
    nb_jours = models.IntegerField(null=True, verbose_name="Nombre de jours au refuge avant adoption")
    animal = models.OneToOneField(Animal, on_delete=models.PROTECT)

    def __str__(self):
        return "Adoption de " + self.animal.nom + " le " + str(self.date)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.animal:
            self.nb_jours = abs((self.date - self.animal.date_arrivee).days)
        return super().save(self, force_insert=force_insert, force_update=force_update, using=using,
                            update_fields=update_fields)
