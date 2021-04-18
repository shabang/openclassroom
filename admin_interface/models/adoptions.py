from _decimal import Decimal

from django.db import models

from .proprietaires import Proprietaire


class Adoption(models.Model):
    date = models.DateField(verbose_name="Date de l'adoption")
    montant = models.DecimalField(
        verbose_name="Montant à payer", max_digits=7, decimal_places=2,
        null=True,
        blank=True,
    )
    montant_restant = models.DecimalField(
        verbose_name="Montant restant à payer",
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
    )
    proprietaire = models.ForeignKey(Proprietaire, on_delete=models.PROTECT)
    nb_jours = models.IntegerField(
        null=True, verbose_name="Nombre de jours au refuge avant adoption"
    )
    animal = models.OneToOneField("Animal", on_delete=models.PROTECT)
    montant_caution_sterilisation = models.DecimalField(
        verbose_name="Si caution pour stérilisation, montant de cette caution :", max_digits=7, decimal_places=2,
        null=True,
        blank=True,
    )
    date_caution_sterilisation = models.DateField(verbose_name="Date d'encaissement de la caution de stérilisation",
                                                  null=True,
                                                  blank=True,
                                                  )
    montant_caution_materiel = models.DecimalField(
        verbose_name="Si caution pour prêt de matériel, montant de cette caution: ", max_digits=7, decimal_places=2,
        null=True,
        blank=True,
    )
    date_caution_materiel = models.DateField(verbose_name="Date d'encaissement de la caution matériel",
                                             null=True,
                                             blank=True,
                                             )
    date_rappel_caution = models.DateField(verbose_name="Date d'envoi du rappel caution",
                                             null=True,
                                             blank=True,
                                             )

    def __str__(self):
        return "Adoption de " + self.animal.nom + " le " + str(self.date)

    def save(self, *args, **kwargs):
        if self.animal and self.animal.date_arrivee:
            self.nb_jours = abs((self.date - self.animal.date_arrivee).days)
        return super().save(*args, **kwargs)

    def get_montant_caution(self):
        if(not self.montant_caution_materiel):
            return self.montant_caution_sterilisation
        if (not self.montant_caution_sterilisation):
            return self.montant_caution_materiel
        return self.montant_caution_materiel + self.montant_caution_sterilisation


    def get_min_date_caution(self):
        if (not self.date_caution_sterilisation):
            return self.date_caution_materiel
        if ( not self.date_caution_materiel
                or self.date_caution_materiel>self.date_caution_sterilisation) :
            return self.date_caution_sterilisation

        return self.date_caution_materiel
