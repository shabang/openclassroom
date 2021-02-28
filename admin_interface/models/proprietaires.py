
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Proprietaire(models.Model):
    date_mise_a_jour = models.DateField(
        verbose_name="Date de mise à jour", auto_now=True
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    adresse = models.CharField(max_length=500)
    code_postal_regex = RegexValidator(
        regex="^[0-9]*$", message="Veuillez entrer un code postal valide."
    )
    code_postal = models.CharField(validators=[code_postal_regex],max_length=5)
    ville = models.CharField(max_length=100)
    telephone_regex = RegexValidator(
        regex="[0-9]{10}", message="Veuillez entrer un numéro de téléphone valide."
    )
    telephone = models.CharField(validators=[telephone_regex], max_length=10)
    deuxieme_telephone = models.CharField(validators=[telephone_regex], max_length=10,blank=True)
    date_inscription = models.DateField(auto_now_add=True)
    inactif = models.BooleanField(default=False,
                                  verbose_name="Desactivé (Ne cocher que si vous ne souhaitez\
                                       plus gérer ce propriétaire dans l'application) ")
    tarif_special = models.BooleanField(default=False,
                                        verbose_name="Ce propriétaire bénéficie t-il de tarifs préférentiels (anciens tarifs)?")
    cadeau_recu = models.BooleanField(default=True,
                                  verbose_name="Cadeau de bienvenu reçu")
    commentaire = models.CharField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        # Au premier enregistrement en base, on définit un login et un mot de passe par défaut
        if self._state.adding:
            self.user.username = (
                slugify(self.user.last_name) + "." + slugify(self.user.first_name)
            )
            self.user.password = make_password(
                slugify(self.user.last_name) + ".password"
            )
            # Pour l'instant on desactive les utilisateurs
            # La partie acces propriétaires est pour plus tard
            self.user.is_active = False
            self.user.save()
        return super(Proprietaire,self).save( *args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def get_adresse_complete(self):
        return f"{self.adresse} \n {self.code_postal} {self.ville}"

class Avoir(models.Model):
    date_obtention = models.DateField(verbose_name="Date d'obtention",blank=True,
        null=True)
    date_utilisation = models.DateField(verbose_name="Date d'utilisation",blank=True,
        null=True)
    montant = models.DecimalField(
        verbose_name="Montant", max_digits=7, decimal_places=2
    )
    commentaire = models.CharField(max_length=500, blank=True)

    proprietaire = models.ForeignKey(
        Proprietaire,
        verbose_name="Propriétaire concerné",
        on_delete=models.PROTECT,
    )

    def utiliser(self):
        self.date_utilisation = timezone.now().date()