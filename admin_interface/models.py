import sys

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from django.utils.text import slugify
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator
from enum import Enum
from django.dispatch import receiver


class TypeAnimalChoice(Enum):
    LAPIN = "Lapin"
    CHINCHILLA = "Chinchilla"
    COCHON_DINDE = "Cochon d'inde"


class TypeSupplementChoice(Enum):
    MEDICAMENT = "Médicament par voie orale/inhalation"
    INJECTION = "Médicament par injection"
    VACCINATION = "Mise à jour d'une vaccination"
    HORAIRE = "Majoration horaire"
    SAMEDI = "Majoration récupération le samedi"
    CAGE = "Supplément cage non fournie"


class SexeChoice(Enum):
    F = "Féminin"
    M = "Masculin"


class EmplacementChoice(Enum):
    PENSION = "Pension"
    REFUGE = "Refuge"


class OrigineChoice(Enum):
    ABANDON = "Abandon particulier"
    REFUGE = "Transfert refuge"
    FOURRIERE = "Fourrière"
    AUTRE = "Autre"


class OuiNonChoice(Enum):
    OUI = "Oui"
    NON = "Non"


class TypeVisiteVetoChoice(Enum):
    VAC = "Vaccination"
    STE = "Stérilisation"
    CHECK = "Checkup"
    AUTRE = "Autre"


class Proprietaire(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    adresse = models.CharField(max_length=500)
    telephone_regex = RegexValidator(regex="[0-9]{10}", message="Veuillez entrer un numéro de téléphone valide.")
    telephone = models.CharField(validators=[telephone_regex], max_length=10)
    date_inscription = models.DateField(auto_now_add=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # Au premier enregistrement en base, on définit un login et un mot de passe par défaut
        if self._state.adding:
            self.user.username = slugify(self.user.last_name) + "." + slugify(self.user.first_name)
            self.user.password = make_password(slugify(self.user.last_name) + ".password")
            self.user.save()
        return models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using,
                                 update_fields=update_fields)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name


class Animal(models.Model):
    nom = models.CharField(max_length=100)
    date_naissance = models.DateField(verbose_name="Date de naissance", null=True, blank=True)
    date_arrivee = models.DateField(verbose_name="Date de première arrivée", null=True, blank=True)
    date_visite = models.DateField(verbose_name="Date de prochaine visite vétérinaire", null=True, blank=True)
    type_animal = models.CharField(max_length=30, verbose_name="Type d'animal",
                                   choices=[(tag.name, tag.value) for tag in TypeAnimalChoice])
    emplacement = models.CharField(max_length=30, verbose_name="Emplacement",
                                   choices=[(tag.name, tag.value) for tag in EmplacementChoice])
    origine = models.CharField(max_length=30, verbose_name="Origine (à remplir uniquement si animal du refuge)",
                               choices=[(tag.name, tag.value) for tag in OrigineChoice], blank=True)
    sexe = models.CharField(max_length=30, verbose_name="Sexe",
                            choices=[(tag.name, tag.value) for tag in SexeChoice])
    sterilise = models.CharField(max_length=30, verbose_name="Stérilisé",
                                 choices=[(tag.name, tag.value) for tag in OuiNonChoice])
    vaccine = models.CharField(max_length=30, verbose_name="Vacciné",
                               choices=[(tag.name, tag.value) for tag in OuiNonChoice])
    date_dernier_vaccin = models.DateField(verbose_name="Date du dernier rappel de vaccin", null=True, blank=True)
    proprietaire = models.ForeignKey(Proprietaire,
                                     verbose_name="Propriétaire (à remplir uniquement si animal de la pension)",
                                     on_delete=models.PROTECT, null=True, blank=True)
    description = models.CharField(max_length=2000, blank=True)

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
            return str(self.get_vaccine_display()) + " (dernier rappel le " + self.date_dernier_vaccin.strftime(
                '%d/%m/%Y') + " )"
        else:
            return self.get_vaccine_display()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # A l'enregistrement de l'animal on met à jour sa date de prochaine visite vétérinaire et ses informations de
        # vaccination
        date_rappel_vaccin = self.date_dernier_vaccin
        date_visites = VisiteMedicale.objects.filter(animaux=self).aggregate(models.Min('date')).get('date__min')
        if date_rappel_vaccin is not None:
            self.vaccine = OuiNonChoice.OUI.name
            if date_visites is not None:
                self.date_visite = date_visites if date_visites < date_rappel_vaccin else date_rappel_vaccin
            else:
                self.date_visite = date_rappel_vaccin
        else:
            self.date_visite = date_visites
        return models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using,
                                 update_fields=update_fields)


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
        return models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using,
                                 update_fields=update_fields)


class VisiteMedicale(models.Model):
    date = models.DateField(verbose_name="Date de la visite")
    type_visite = models.CharField(max_length=30, verbose_name="Objet de la visite",
                                   choices=[(tag.name, tag.value) for tag in TypeVisiteVetoChoice])
    commentaire = models.CharField(max_length=2000, blank=True)
    montant = models.DecimalField(verbose_name="Montant", max_digits=7, decimal_places=2, blank=True, null=True)
    animaux = models.ManyToManyField(Animal)

    def __str__(self):
        return "visite " + str(self.type_visite) + " le " + str(self.date)

@receiver(m2m_changed, sender = VisiteMedicale.animaux.through)
def visite_medicale_save_action(sender, instance, **kwargs):
   # Instance est une visite médicale
    if instance.type_visite in (TypeVisiteVetoChoice.STE.name, TypeVisiteVetoChoice.VAC.name):
        for animal in instance.animaux.all():
            if instance.type_visite == TypeVisiteVetoChoice.STE.name:
                animal.sterilise = OuiNonChoice.OUI.name
            elif instance.type_visite == TypeVisiteVetoChoice.VAC.name:
                animal.vaccine = OuiNonChoice.OUI.name
                animal.date_dernier_vaccin = instance.date
            animal.save()

class Sejour(models.Model):
    date_arrivee = models.DateTimeField(verbose_name="Date d'arrivée")
    date_depart = models.DateTimeField(verbose_name="Date de départ")
    nb_cages_fournies = models.IntegerField(verbose_name="Nombre de cages fournies par le propriétaire ", default=1)
    nb_cages_a_fournir = models.IntegerField(
        verbose_name="Nombre de cages à fournir par la pension (supplément de 1€/cage/jour) ", default=0)
    montant = models.DecimalField(verbose_name="Montant à payer", max_digits=7, decimal_places=2, blank=True, null=True)
    montant_restant = models.DecimalField(verbose_name="Montant restant à payer", max_digits=7, decimal_places=2,
                                          blank=True, null=True)
    nb_jours = models.IntegerField()
    animaux = models.ManyToManyField(Animal)
    proprietaire = models.ForeignKey(Proprietaire, on_delete=models.PROTECT, null=True)
    vaccination = models.CharField(max_length=3,
                                   verbose_name="Tous les animaux du séjour sont correctement vaccinés pour toute la "
                                                "durée du séjour? (majoration de 90€ si ce n'est pas le cas) ",
                                   choices=[(tag.name, tag.value) for tag in OuiNonChoice], default=OuiNonChoice.OUI.name)
    soin = models.CharField(max_length=3,
                            verbose_name="Un de vos animaux nécessite un soin quotidien (a préciser ci-dessous) ",
                            choices=[(tag.name, tag.value) for tag in OuiNonChoice], default=OuiNonChoice.NON.name)
    injection = models.CharField(max_length=3, verbose_name="Le soin quotidien de votre animal se fait par injection ",
                                 choices=[(tag.name, tag.value) for tag in OuiNonChoice], default=OuiNonChoice.NON.name)
    commentaire = models.CharField(max_length=1000,
                                   verbose_name="Indications sur le séjour (soins divers, points d'attention...)",
                                   blank=True)

    def __str__(self):
        return "Séjour du " + self.date_arrivee.strftime('%d/%m/%Y %H:%M') + " au " + self.date_depart.strftime(
            '%d/%m/%Y %H:%M')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.nb_jours = abs((self.date_depart - self.date_arrivee).days)
        return models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using,
                                 update_fields=update_fields)


class TarifJournalier(models.Model):
    type_animal = models.CharField(max_length=30, verbose_name="Type d'animal",
                                   choices=[(tag.name, tag.value) for tag in TypeAnimalChoice])
    adopte_refuge = models.CharField(max_length=3, verbose_name="Adopté au refuge",
                                     choices=[(tag.name, tag.value) for tag in OuiNonChoice])
    supplementaire = models.CharField(max_length=3, verbose_name="Animal supplémentaire dans la même cage",
                                      choices=[(tag.name, tag.value) for tag in OuiNonChoice])
    montant_jour = models.DecimalField(verbose_name="Prix par jour", max_digits=7, decimal_places=2)

    def __str__(self):
        return "Tarif journalier pour " + self.type_animal


class TarifAdoption(models.Model):
    type_animal = models.CharField(max_length=30, verbose_name="Type d'animal",
                                   choices=[(tag.name, tag.value) for tag in TypeAnimalChoice])
    sexe = models.CharField(max_length=30, verbose_name="Sexe", choices=[(tag, tag.value) for tag in SexeChoice])
    sterilise = models.CharField(max_length=3, verbose_name="Stérilisé",
                                 choices=[(tag.name, tag.value) for tag in OuiNonChoice])
    montant_adoption = models.DecimalField(verbose_name="Prix par jour", max_digits=7, decimal_places=2)

    def __str__(self):
        return "Tarif adoption pour " + self.type_animal


class ParametreTarifairePension(models.Model):
    type_supplement = models.CharField(max_length=50, verbose_name="Libellé du supplément",
                                       choices=[(tag.name, tag.value) for tag in TypeSupplementChoice])
    supplement_journalier = models.CharField(max_length=3, verbose_name="Supplément journalier?",
                                             choices=[(tag.name, tag.value) for tag in OuiNonChoice])
    montant = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return "Supplément tarifaire pour  " + self.type_supplement
