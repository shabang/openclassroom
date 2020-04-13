from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from admin_interface.forms import (
    AdoptionForm,
    AdoptionFormNoProprietaire,
    AdoptionUpdateForm,
    ProprietaireForm,
    UserForm,
)
from admin_interface.models import EmplacementChoice
from admin_interface.models.adoptions import Adoption
from admin_interface.models.animaux import Animal
from admin_interface.models.tarifs import TarifAdoption


class UpdateAdoption(LoginRequiredMixin, UpdateView):
    model = Adoption
    template_name = 'admin_interface/update_adoption.html'
    form_class = AdoptionUpdateForm

    def get_success_url(self):
        return reverse_lazy('detail_animal', kwargs={'pk': self.object.animal.id})


@login_required
def index(request, pk):
    animal = Animal.objects.get(id=pk)
    return render(request, 'admin_interface/adoption.html', locals())


@login_required
def adoption_complete(request, pk):
    animal = Animal.objects.get(id=pk)
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        proprietaire_form = ProprietaireForm(data=request.POST)
        adoption_form = AdoptionFormNoProprietaire(data=request.POST)
        if user_form.is_valid() and proprietaire_form.is_valid() and adoption_form.is_valid():
            # A l'enregistreent de l'utilisateur, identifiant et mot de passe sont autaumatiquement calculés
            user = user_form.save()

            proprietaire = proprietaire_form.save(commit=False)
            proprietaire.user = user
            proprietaire.save()

            # On rattache le nouveau proprietaire à l'adoption
            adoption = adoption_form.save(commit=False)
            adoption.proprietaire = proprietaire
            adoption.animal = animal
            adoption.save()

            # l'animal ne fait plus partie du refuge
            animal.emplacement = EmplacementChoice.PENSION.name
            animal.proprietaire = proprietaire
            animal.save()

            return redirect('detail_animal', pk=animal.id)

    else:
        user_form = UserForm()
        proprietaire_form = ProprietaireForm()
        adoption_form = AdoptionFormNoProprietaire()
        montant_adoption = get_montant_adoption(animal)
        if montant_adoption:
            adoption_form.fields['montant'].initial = montant_adoption
            adoption_form.fields['montant_restant'].initial = montant_adoption

    return render(request, 'admin_interface/adoption_complete.html', locals())


@login_required
def adoption_allegee(request, pk):
    animal = Animal.objects.get(id=pk)
    if request.method == 'POST':
        adoption_form = AdoptionForm(data=request.POST)
        if adoption_form.is_valid():
            # On rattache le nouveau proprietaire à l'adoption
            new_adoption = adoption_form.save(commit=False)

            # l'animal ne fait plus partie du refuge
            new_adoption.animal = animal
            new_adoption.save()
            animal.emplacement = EmplacementChoice.PENSION.name
            animal.proprietaire = new_adoption.proprietaire
            animal.save()

            return redirect('detail_animal', pk=animal.id)

    else:
        adoption_form = AdoptionForm()
        montant_adoption = get_montant_adoption(animal)
        adoption_form.fields['montant'].initial = montant_adoption
        adoption_form.fields['montant_restant'].initial = montant_adoption
    return render(request, 'admin_interface/adoption_allegee.html', locals())


def get_montant_adoption(animal):
    try:
        tarif_applicable = TarifAdoption.objects.get(type_animal=animal.type_animal, sexe=animal.sexe,
                                                     sterilise=animal.sterilise)
        return tarif_applicable.montant_adoption
    except TarifAdoption.DoesNotExist:
        return None
