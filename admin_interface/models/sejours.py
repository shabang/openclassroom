from django.db import models

from . import OuiNonChoice
from .animaux import Animal
from .proprietaires import Proprietaire


class Sejour(models.Model):
    date_mise_a_jour = models.DateField(
        verbose_name="Date de mise à jour", auto_now=True
    )
    date_arrivee = models.DateTimeField(verbose_name="Date d'arrivée")
    date_depart = models.DateTimeField(verbose_name="Date de départ")
    nb_cages_fournies = models.IntegerField(
        verbose_name="Nombre de cages fournies par le propriétaire ", default=1
    )
    nb_cages_a_fournir = models.IntegerField(
        verbose_name="Nombre de cages à fournir par la pension (supplément de 1€/cage/jour) ",
        default=0,
    )
    montant = models.DecimalField(
        verbose_name="Montant à payer",
        max_digits=7,
        decimal_places=2,
        blank=True,
        null=True,
    )
    arrhes = models.DecimalField(
        verbose_name="Montant arrhes",
        max_digits=7,
        decimal_places=2,
        blank=True,
        null=True,
    )
    montant_restant = models.DecimalField(
        verbose_name="Montant restant à payer",
        max_digits=7,
        decimal_places=2,
        blank=True,
        null=True,
    )
    nb_jours = models.IntegerField()
    animaux = models.ManyToManyField(Animal)
    proprietaire = models.ForeignKey(Proprietaire, on_delete=models.PROTECT, null=True)
    vaccination = models.CharField(
        max_length=3,
        verbose_name="Tous les animaux du séjour sont correctement vaccinés pour toute la "
        "durée du séjour? (majoration de 90€ si ce n'est pas le cas) ",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
        default=OuiNonChoice.OUI.name,
    )
    soin = models.CharField(
        max_length=3,
        verbose_name="Un de vos animaux nécessite un soin quotidien (a préciser ci-dessous) ",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
        default=OuiNonChoice.NON.name,
    )
    injection = models.CharField(
        max_length=3,
        verbose_name="Le soin quotidien de votre animal se fait par injection ",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
        default=OuiNonChoice.NON.name,
    )
    commentaire = models.CharField(
        max_length=1000,
        verbose_name="Indications sur le séjour (soins divers, points d'attention...)",
        blank=True,
    )
    annule = models.BooleanField(default=False,
                                  verbose_name="Séjour annulé")

    def __str__(self):
        if self.date_arrivee and self.date_depart:
            return f"Séjour du {self.date_arrivee:%d/%m/%Y %H:%M} au {self.date_depart:%d/%m/%Y %H:%M}"
        return ""

    def save(self, *args, **kwargs):
        self.nb_jours = abs((self.date_depart - self.date_arrivee).days)
        return super().save(*args, **kwargs)

    def annulation(self):
        self.annule = True
