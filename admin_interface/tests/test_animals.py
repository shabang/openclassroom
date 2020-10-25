import unittest

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse_lazy, reverse

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
        self.client.post('/accounts/login/', {'username': 'dupont.jean', 'password': 'dupont.password'})

    def test_username(self):
        #Vérification de la génération du username
        self.assertEqual(self.proprietaire.user.username, "dupont.jean")

    def test_animal_list_view(self):
        # Vérification que les deux animaux sont listés dans la liste des animaux
        response = self.client.get(reverse_lazy('animals'))
        self.assertContains(response, "Lapin refuge")
        self.assertContains(response, "Lapin pension")

    def test_animal_detail_view(self):
        # Vérification de la vue de détail d'un animal
        response = self.client.get(reverse('detail_animal', args=[self.animal_pension.id]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('detail_animal', args=[self.animal_refuge.id]))
        self.assertEqual(response.status_code, 200)

    def test_proprietaire_form_view(self):
        #Vérification de l'accès au formulaire de création d'un animal
        response = self.client.get(reverse_lazy('creer_animal'))
        self.assertEqual(response.status_code, 200)
        #Vérification de l'accès au formulaire de modification d'un animal
        response = self.client.get(reverse_lazy('modifier_animal', kwargs={"pk": self.animal_refuge.id}))
        self.assertEqual(response.status_code, 200)