from django.db import models

TYPE_DEMANDE = (
    ('LAPIN',"Lapin"),
    ('HAMSTER',"Hamster"),
    ('COCHON_DINDE',"Cochon d'inde"),
    ('',"")
)

SEXE = (
    ('F', "Féminin"),
    ('M', "Masculin")
)

ORIGINE = (
    ('PENSION', "Pension"),
    ('REFUGE', "Refuge"),
    ('',"")
)

OUI_NON = (
    ('OUI', "Oui"),
    ('NON', "Non")
)

TYPE_VETO = (
    ('VAC', "Vaccination"),
    ('STE', "Stérilisation"),
    ('CHECK', "Checkup"),
    ('AUTRE', "Autre")
)

class Proprietaire(models.Model):
    nom = models.CharField(max_length=100, null=True)
    prenom = models.CharField(max_length=100, null=True)
    mail = models.CharField(max_length=200, verbose_name = "Adresse mail", null=True)
    adresse = models.CharField(max_length=500, null=True)
    telephone = models.CharField(max_length=15, verbose_name = "Numéro de téléphone", null=True)
    
    def __str__(self):
        return self.prenom + " " + self.nom
        
class Adoption(models.Model):
    date = models.DateTimeField(verbose_name = "Date de l'adoption")
    montant = models.DecimalField(verbose_name="Montant à payer" , max_digits=7, decimal_places=2, null=True)
    montant_restant = models.DecimalField(verbose_name="Montant restant à payer" , max_digits=7, decimal_places=2, null=True)
    
    def __str__(self):
        return "Adoption de " + self.animal.nom + " le " + str(self.date)

class Animal(models.Model):
    nom = models.CharField(max_length=100)
    date_naissance = models.DateTimeField(verbose_name = "Date de naissance", null=True)
    date_arrivee = models.DateTimeField(verbose_name = "Date de première arrivée", null=True)
    date_visite = models.DateTimeField(verbose_name = "Date de prochaine visite vétérinaire", null=True)
    date_adoption = models.DateTimeField(verbose_name = "Date d'adoption", null=True)
    description = models.CharField(max_length=2000, null=True)
    type_animal = models.CharField(max_length=30, verbose_name="Type d'animal",choices=TYPE_DEMANDE)
    sexe = models.CharField(max_length=30, verbose_name="Sexe",choices=SEXE)
    origine = models.CharField(max_length=30, verbose_name="Origine",choices=ORIGINE, null=True)
    sterilise = models.CharField(max_length=30, verbose_name="Stérilisé",choices=OUI_NON, null=True)
    vaccine = models.CharField(max_length=30, verbose_name="Vacciné",choices=OUI_NON, null=True)
    proprietaire = models.ForeignKey(Proprietaire, on_delete=models.PROTECT, null=True)
    adoption = models.OneToOneField(Adoption, on_delete=models.PROTECT, null=True)
    
    def __str__(self):
        return self.nom
        
    def isFromPension(self):
         return self.origine == 'PENSION'

class VisiteMedicale(models.Model):
    date = models.DateTimeField(auto_now_add = True, verbose_name = "Date de la visite")
    type_visite = models.CharField(max_length=30, verbose_name="Objet de la visite",choices=TYPE_VETO, null=True)
    commentaire = models.CharField(max_length=2000, null=True)
    animal = models.ForeignKey(Animal, on_delete=models.PROTECT, null=True)
    
    def __str__(self):
        return "visite " + self.type_visite + " le " + self.date
        
        
class Sejour(models.Model):
    date_arrivee = models.DateTimeField(auto_now_add = True, verbose_name = "Date d'arrivée", null=True)
    date_depart = models.DateTimeField(verbose_name = "Date de départ", null=True)
    cage = models.CharField(max_length=30, verbose_name="Cage fournie",choices=OUI_NON, null=True)
    montant = models.DecimalField(verbose_name="Montant à payer" , max_digits=7, decimal_places=2, null=True)
    montant_restant = models.DecimalField(verbose_name="Montant restant à payer" , max_digits=7, decimal_places=2, null=True)
    animal = models.ForeignKey(Animal, on_delete=models.PROTECT, null=True)
    
    def __str__(self):
        return "Séjour du " + self.date_arrivee + " au " + self.date_depart
