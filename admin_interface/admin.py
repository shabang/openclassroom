from django.contrib import admin
from django.contrib.auth.models import User
from import_export.resources import ModelResource

from admin_interface.models.adoptions import Adoption
from admin_interface.models.animaux import Animal
from admin_interface.models.proprietaires import Proprietaire
from admin_interface.models.sejours import Sejour
from admin_interface.models.tarifs import (
    ParametreTarifairePension,
    TarifAdoption,
    TarifJournalier,
)
from admin_interface.models.visite_medicales import VisiteMedicale
from import_export.admin import ImportExportModelAdmin


class ProprietaireResource(ModelResource):

    class Meta:
        model = Proprietaire


@admin.register(Proprietaire)
class ProprietaireAdmin(ImportExportModelAdmin):
    resource_class = ProprietaireResource

admin.site.unregister(User)

@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    pass


@admin.register(Animal)
class AnimalAdmin(ImportExportModelAdmin):
    pass


@admin.register(VisiteMedicale)
class VisiteMedicaleAdmin(ImportExportModelAdmin):
    pass


@admin.register(Sejour)
class SejourAdmin(ImportExportModelAdmin):
    pass


@admin.register(Adoption)
class AdoptionAdmin(ImportExportModelAdmin):
    pass


@admin.register(TarifJournalier)
class TarifJournalierAdmin(ImportExportModelAdmin):
    pass


@admin.register(ParametreTarifairePension)
class ParametreTarifairePensionAdmin(ImportExportModelAdmin):
    pass


@admin.register(TarifAdoption)
class TarifAdoptionAdmin(ImportExportModelAdmin):
    pass
