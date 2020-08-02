import unittest

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse_lazy

from admin_interface.models.animaux import Animal
from admin_interface.models.proprietaires import Proprietaire


def create_proprietaire():
    """
    Création d'un propriétaire avec son nom et prénom
    """
    user = User.objects.create(first_name="Jean", last_name="Dupont",
                               email="test@test.fr")
    return Proprietaire.objects.create(user=user, adresse="Adresse test",
                                       telephone="0344567788")


def create_animal_pension(proprietaire):
    #Création d'un animal de la pension
    animal = Animal.objects.create(nom="Lapin pension",type_animal="LAPIN", emplacement="PENSION",
                                   sexe="F", sterilise="OUI",vaccine="NON", proprietaire = proprietaire)
    return animal

def create_animal_refuge():
    # Création d'un animal de la pension
    animal = Animal.objects.create(nom="Lapin refuge", type_animal="LAPIN", emplacement="REFUGE",
                                   sexe="F", sterilise="OUI", vaccine="NON")
    return animal

class AnimalTests(TestCase):
    def setUp(self):
        self.proprietaire = create_proprietaire()
        self.proprietaire.user.is_active = True
        self.proprietaire.user.save()
        self.animal_pension = create_animal_pension(self.proprietaire)
        self.animal_refuge = create_animal_refuge()
        self.client = Client()

    def test_username(self):
        #Vérification de la génération du username
        self.assertEqual(self.proprietaire.user.username, "dupont.jean")

    def test_animal_list_view(self):
        # Vérification que les deux animaux sont listés dans la liste des animaux
        self.client.post('/accounts/login/', {'username': 'dupont.jean', 'password': 'dupont.password'})
        response = self.client.get(reverse_lazy('animals'))
        self.assertContains(response, "Lapin refuge")
        self.assertContains(response, "Lapin pension")