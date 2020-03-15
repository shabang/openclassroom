from django.contrib import admin
from applicationTest.models import Proprietaire, Animal, VisiteMedicale, Sejour, Adoption,\
TarifJournalier, TarifAdoption, ParametreTarifairePension

admin.site.register(Proprietaire)
admin.site.register(Animal)
admin.site.register(VisiteMedicale)
admin.site.register(Sejour)
admin.site.register(Adoption)
admin.site.register(TarifJournalier)
admin.site.register(TarifAdoption)
admin.site.register(ParametreTarifairePension)