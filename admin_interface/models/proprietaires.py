from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify


class Proprietaire(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    adresse = models.CharField(max_length=500)
    telephone_regex = RegexValidator(
        regex="[0-9]{10}", message="Veuillez entrer un numéro de téléphone valide."
    )
    telephone = models.CharField(validators=[telephone_regex], max_length=10)
    date_inscription = models.DateField(auto_now_add=True)

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
