from django.contrib import admin
from django.contrib.auth.models import User
from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

from admin_interface.models.adoptions import Adoption
from admin_interface.models.animaux import Animal, HistoriquePoids
from admin_interface.models.proprietaires import Proprietaire, Avoir
from admin_interface.models.sejours import Sejour
from admin_interface.models.tarifs import (
    ParametreTarifairePension,
    TarifAdoption,
    TarifJournalier,
)
from admin_interface.models.visite_medicales import VisiteMedicale
from import_export.admin import ImportExportModelAdmin


class ProprietaireResource(ModelResource):
    user = Field(column_name='user', attribute='user', widget=ForeignKeyWidget(User, 'username'))
    class Meta:
        model = Proprietaire
        fields = ('id','user','adresse','telephone','code_postal','ville')

class AnimalResource(ModelResource):
    proprietaire = Field(column_name='proprietaire', attribute='proprietaire',
                         widget=ForeignKeyWidget(Proprietaire, 'user__username'))
    class Meta:
        model = Animal
        fields = ('id', 'nom', 'date_naissance', 'date_arrivee', 'date_visite', 'type_animal', 'emplacement',
                  'origine', 'sexe', 'sterilise', 'vaccine', 'date_dernier_vaccin', 'date_sterilisation',
                  'poids', 'proprietaire', 'description', 'sante', 'inactif')

class AdoptionResource(ModelResource):
    proprietaire = Field(column_name='proprietaire', attribute='proprietaire',
                         widget=ForeignKeyWidget(Proprietaire, 'user__username'))
    animal = Field(column_name='nom', attribute='animal',
                         widget=ForeignKeyWidget(Animal, 'nom'))
    class Meta:
        model = Adoption
        fields = ('id', 'proprietaire', 'date','nom','montant')

class SejourResource(ModelResource):
    proprietaire = Field(column_name='proprietaire', attribute='proprietaire',
                         widget=ForeignKeyWidget(Proprietaire, 'user__username'))
    animaux = Field(column_name='animaux', attribute='animaux',
                         widget=ManyToManyWidget(Animal,",", 'nom'))
    class Meta:
        model = Sejour
        fields = ('id', 'proprietaire', 'date_arrivee','date_depart','nb_cages_fournies',
                  'nb_cages_a_fournir','animaux','montant','montant_restant','vaccination',
                  'soin','injection','commentaire')


@admin.register(Proprietaire)
class ProprietaireAdmin(ImportExportModelAdmin):
    resource_class = ProprietaireResource

admin.site.unregister(User)

@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    pass


@admin.register(Animal)
class AnimalAdmin(ImportExportModelAdmin):
    resource_class = AnimalResource


@admin.register(VisiteMedicale)
class VisiteMedicaleAdmin(ImportExportModelAdmin):
    pass


@admin.register(Sejour)
class SejourAdmin(ImportExportModelAdmin):
    resource_class = SejourResource


@admin.register(Adoption)
class AdoptionAdmin(ImportExportModelAdmin):
    resource_class = AdoptionResource


@admin.register(TarifJournalier)
class TarifJournalierAdmin(ImportExportModelAdmin):
    pass

@admin.register(Avoir)
class AvoirAdmin(ImportExportModelAdmin):
    pass


@admin.register(ParametreTarifairePension)
class ParametreTarifairePensionAdmin(ImportExportModelAdmin):
    pass


@admin.register(TarifAdoption)
class TarifAdoptionAdmin(ImportExportModelAdmin):
    pass

@admin.register(HistoriquePoids)
class HistoriquePoidsAdmin(ImportExportModelAdmin):
    pass
