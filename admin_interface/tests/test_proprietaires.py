# from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.utils import timezone

from admin_interface.models.proprietaires import Proprietaire


def create_proprietaire(first_name, last_name):
    """
    Création d'un propriétaire avec son nom et prénom
    """
    user = User.objects.create(first_name=first_name, last_name=last_name,
                               email="test@test.fr")
    return Proprietaire.objects.create(user=user, adresse="Adresse test",
                                       telephone="0344567788")


class ProprietaireCreationTests(TestCase):
    def setUp(self):
        self.proprietaire = create_proprietaire("Jean", "Dupont")

    def test_username(self):
        self.assertEqual(self.proprietaire.user.username, "dupont.jean")

    def test_password(self):
        self.assertFalse(self.proprietaire.user.password is None)