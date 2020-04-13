from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from admin_interface.models.tarifs import TarifJournalier, ParametreTarifairePension, TarifAdoption


@login_required
def parametrage_tarifaire(request):
    selected = "parametrage_tarifaire"
    tarifs_journaliers_pension = TarifJournalier.objects.all()
    tarifs_supplements = ParametreTarifairePension.objects.all()
    tarifs_adoption = TarifAdoption.objects.all()
    return render(request, 'admin_interface/parametrage_tarifaire.html', locals())
