from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from applicationTest.models import Proprietaire, Animal, VisiteMedicale, Sejour, Adoption,\
TarifJournalier, TarifAdoption, ParametreTarifairePension

admin.site.register(Proprietaire)
admin.site.register(Animal)
admin.site.register(VisiteMedicale)
admin.site.register(Sejour)
admin.site.register(Adoption)

@admin.register(TarifJournalier)
class TarifJournalierAdmin(ImportExportModelAdmin):
    pass

@admin.register(ParametreTarifairePension)
class ParametreTarifairePensionAdmin(ImportExportModelAdmin):
    pass

@admin.register(TarifAdoption)
class TarifAdoptionAdmin(ImportExportModelAdmin):
    pass