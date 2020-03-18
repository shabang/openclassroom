from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.contrib.auth.hashers import make_password


TYPE_ANIMAL = (
    ('LAPIN',"Lapin"),
    ('CHINCHILLA','Chinchilla'),
    ('COCHON_DINDE',"Cochon d'inde"),
)

TYPE_SUPPLEMENT = (
    ('MEDICAMENT',"Médicament par voie orale/inhalation"),
    ('INJECTION',"Médicament par injection"),
    ('VACCINATION',"Mise à jour d'une vaccination"),
    ('HORAIRE',"Majoration horaire"),
    ('SAMEDI',"Majoration récupération le samedi"),
    ('CAGE',"Supplément cage non fournie"),
)

SEXE = (
    ('F', "Féminin"),
    ('M', "Masculin")
)

ORIGINE = (
    ('PENSION', "Pension"),
    ('REFUGE', "Refuge"),
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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    adresse = models.CharField(max_length=500, null=True)
    telephone = models.CharField(max_length=15, verbose_name = "Numéro de téléphone", null=True)
    date_inscription = models.DateField(auto_now_add=True)
    
    def save(self, force_insert=False, force_update=False, using=None, 
        update_fields=None):
        #Au premier enregistrement en base, on définit un login et un mot de passe par défaut
        if (self._state.adding):
            self.user.username = slugify(self.user.last_name)+"."+slugify(self.user.first_name)
            self.user.password = make_password(slugify(self.user.last_name)+".password")
            self.user.save()
        return models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
    
    def __str__(self):
        return self.user.first_name + " " + self.user.last_name
        
class Adoption(models.Model):
    date = models.DateField(verbose_name = "Date de l'adoption", null = True)
    montant = models.DecimalField(verbose_name="Montant à payer" , max_digits=7, decimal_places=2, null=True)
    montant_restant = models.DecimalField(verbose_name="Montant restant à payer" , max_digits=7, decimal_places=2, blank=True)
    proprietaire = models.ForeignKey(Proprietaire, on_delete=models.PROTECT)
    def __str__(self):
        return "Adoption de " + self.animal.nom + " le " + str(self.date)

class Animal(models.Model):
    nom = models.CharField(max_length=100)
    date_naissance = models.DateField(verbose_name = "Date de naissance", blank = True, null=True)
    date_arrivee = models.DateField(verbose_name = "Date de première arrivée", blank = True, null=True)
    date_visite = models.DateField(verbose_name = "Date de prochaine visite vétérinaire", blank = True, null=True)
    type_animal = models.CharField(max_length=30, verbose_name="Type d'animal",choices=TYPE_ANIMAL)
    origine = models.CharField(max_length=30, verbose_name="Origine",choices=ORIGINE)
    sexe = models.CharField(max_length=30, verbose_name="Sexe",choices=SEXE)
    sterilise = models.CharField(max_length=30, verbose_name="Stérilisé",choices=OUI_NON, null=True)
    vaccine = models.CharField(max_length=30, verbose_name="Vacciné",choices=OUI_NON, null=True)
    date_dernier_vaccin = models.DateField(verbose_name = "Date du dernier rappel de vaccin", null=True, blank = True)
    proprietaire = models.ForeignKey(Proprietaire, on_delete=models.PROTECT, null=True, blank=True)
    adoption = models.OneToOneField(Adoption, on_delete=models.PROTECT, null=True, blank=True)
    description = models.CharField(max_length=2000, blank=True)

    def __str__(self):
        return self.nom
        
    def isFromPension(self):
         return self.origine == 'PENSION'
     
    def isFromRefuge(self):
        return self.origine == 'REFUGE'
     
    def getVaccinStr(self):
        return self.get_vaccine_display + " (dernier rappel le " + str(self.date_dernier_vaccin) + " )" 
    
    def save(self, force_insert=False, force_update=False, using=None, 
        update_fields=None):
        #A l'enregistrement de l'animal on met à jour sa date de prochaine visite vétérinaire et ses informations de vaccination
        date_rappel_vaccin = self.date_dernier_vaccin
        date_visites = VisiteMedicale.objects.filter(animaux=self).aggregate(models.Min('date')).get('date__min')
        if (date_rappel_vaccin!=None):
            self.vaccine = "OUI"
            if (date_visites!=None):
                self.date_visite = date_visites if date_visites.date() < date_rappel_vaccin else date_rappel_vaccin
            else :
                self.date_visite =  date_rappel_vaccin
        else:
            self.date_visite =   date_visites
        return models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

class VisiteMedicale(models.Model):
    date = models.DateTimeField(verbose_name = "Date de la visite")
    type_visite = models.CharField(max_length=30, verbose_name="Objet de la visite",choices=TYPE_VETO, null=True)
    commentaire = models.CharField(max_length=2000, null=True, blank = True)
    montant = models.DecimalField(verbose_name="Montant" , max_digits=7, decimal_places=2, null=True)
    animaux = models.ManyToManyField(Animal)
    
    def __str__(self):
        return "visite " + str(self.type_visite) + " le " + str(self.date)
        
        
class Sejour(models.Model):
    date_arrivee = models.DateTimeField(verbose_name = "Date d'arrivée", null=True, blank = True)
    date_depart = models.DateTimeField(verbose_name = "Date de départ", null=True)
    nb_cages_fournies = models.IntegerField(verbose_name="Nombre de cages fournies par le propriétaire ",default=1)
    nb_cages_a_fournir =  models.IntegerField(verbose_name="Nombre de cages à fournir par la pension (supplément de 1€/cage/jour) ",default=0)
    montant = models.DecimalField(verbose_name="Montant à payer" , max_digits=7, decimal_places=2, null=True, blank=True)
    montant_paye = models.DecimalField(verbose_name="Montant payé" , max_digits=7, decimal_places=2, null=True, blank=True)
    montant_restant = models.DecimalField(verbose_name="Montant restant à payer" , max_digits=7, decimal_places=2, null=True, blank = True)
    nb_jours = models.IntegerField()
    animaux = models.ManyToManyField(Animal)
    proprietaire = models.ForeignKey(Proprietaire, on_delete=models.PROTECT, null=True) 
    vaccination = models.CharField(max_length=3, verbose_name="Tous les animaux du séjour sont correctement vaccinés pour toute la durée du séjour? (majoration de 90€ si ce n'est pas le cas) : ",choices=OUI_NON, default="OUI")
    soin = models.CharField(max_length=3, verbose_name="Un de vos animaux nécessite un soin quotidien (a préciser ci-dessous) ",choices=OUI_NON, default="NON")
    injection = models.CharField(max_length=3, verbose_name="Le soin quotidien de votre animal se fait par injection ",choices=OUI_NON, default="NON")
    commentaire = models.CharField(max_length=1000, verbose_name = "Indications sur le séjour (soins divers, points d'attention...)", blank = True, null=True)
    
    def __str__(self):
        return "Séjour du " + self.date_arrivee.strftime('%d/%m/%Y %H:%M') + " au " + self.date_depart.strftime('%Y-%m-%d %H:%M')
    
    def save(self, force_insert=False, force_update=False, using=None, 
        update_fields=None):
        self.nb_jours = abs((self.date_depart - self.date_arrivee).days)
        return models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

class TarifJournalier(models.Model):
    type_animal = models.CharField(max_length=30, verbose_name="Type d'animal",choices=TYPE_ANIMAL)
    adopte_refuge = models.CharField(max_length=3, verbose_name="Adopté au refuge",choices=OUI_NON)
    supplementaire = models.CharField(max_length=3, verbose_name="Animal supplémentaire dans la même cage",choices=OUI_NON)
    montant_jour = models.DecimalField(verbose_name="Prix par jour",  max_digits=7, decimal_places=2)
    
class TarifAdoption(models.Model):
    type_animal = models.CharField(max_length=30, verbose_name="Type d'animal",choices=TYPE_ANIMAL)
    sexe = models.CharField(max_length=30, verbose_name="Sexe",choices=SEXE)
    sterilise = models.CharField(max_length=3, verbose_name="Stérilisé",choices=OUI_NON)
    montant_adoption = models.DecimalField(verbose_name="Prix par jour",  max_digits=7, decimal_places=2)
    
class ParametreTarifairePension(models.Model):
    type_supplement = models.CharField(max_length=50, verbose_name="Libellé du supplément",choices=TYPE_SUPPLEMENT)
    supplement_journalier = models.CharField(max_length=3, verbose_name="Supplément journalier?",choices=OUI_NON)
    montant = models.DecimalField(max_digits=7, decimal_places=2)
    
    