
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse, reverse_lazy

from admin_interface.models.proprietaires import Proprietaire


def create_proprietaire(first_name, last_name):
    """
    Création d'un propriétaire avec son nom et prénom
    """
    user = User.objects.create(first_name=first_name, last_name=last_name,
                               email="test@test.fr",is_active=True, is_staff=True)
    return Proprietaire.objects.create(user=user, adresse="Adresse test",
                                       telephone="0344567788")


class ProprietaireTests(TestCase):
    def setUp(self):
        self.proprietaire = create_proprietaire("Jean", "Dupont")
        self.client = Client()
        self.proprietaire.user.is_active = True
        self.proprietaire.user.save()

    def test_username(self):
        #Vérification de la génération du username
        self.assertEqual(self.proprietaire.user.username, "dupont.jean")

    def test_password(self):
        #Vérification qu'on mot de passe a été généré
        self.assertFalse(self.proprietaire.user.password is None)

    def test_proprietaire_list_view(self):
        #Vérification que le propriétaire est listé dans la liste des propriétaires
        self.client.post('/accounts/login/', {'username':'dupont.jean', 'password':'dupont.password'})
        response =  self.client.get(reverse_lazy('proprietaires'))
        self.assertContains(response,"Dupont")

    def test_proprietaire_detail_view(self):
        #Vérification de la vue de détail du propriétaire
        self.client.post('/accounts/login/', {'username': 'dupont.jean', 'password': 'dupont.password'})
        response = self.client.get(reverse('detail_proprietaire', args=[self.proprietaire.id]))
        self.assertEqual(response.status_code, 200)

    def test_proprietaire_form_view(self):
        self.client.post('/accounts/login/', {'username': 'dupont.jean', 'password': 'dupont.password'})
        #Vérification de l'accès au formulaire de création d'un proprietaire
        response = self.client.get(reverse_lazy('creer_proprietaire'))
        self.assertEqual(response.status_code, 200)
        #Vérification de l'accès au formulaire de modification d'un proprietaire
        response = self.client.get(reverse_lazy('modifier_proprietaire', kwargs={"pk": self.proprietaire.id}))
        self.assertEqual(response.status_code, 200)