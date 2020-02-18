from django.contrib import admin
from applicationTest.models import Proprietaire, Animal, VisiteMedicale, Sejour, Adoption

admin.site.register(Proprietaire)
admin.site.register(Animal)
admin.site.register(VisiteMedicale)
admin.site.register(Sejour)
admin.site.register(Adoption)