from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render

from admin_interface.forms import ProprietaireForm, UserForm, ProprietaireSearchForm
from admin_interface.models.proprietaires import Proprietaire


@login_required
def create_proprietaire(request):
    formulaire_valide = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        proprietaire_form = ProprietaireForm(data=request.POST)
        if user_form.is_valid() and proprietaire_form.is_valid():
            # A l'enregistreent de l'utilisateur, identifiant et mot de passe sont autaumatiquement calculés
            user = user_form.save()

            proprietaire = proprietaire_form.save(commit=False)
            proprietaire.user = user
            proprietaire.save()

            formulaire_valide = True
            return redirect('detail_proprietaire', pk=proprietaire.id)

    else:
        user_form = UserForm()
        proprietaire_form = ProprietaireForm()
    # Render the template depending on the context.
    return render(request, 'admin_interface/proprietaire_form.html', locals())


@login_required
def update_proprietaire(request, pk):
    proprietaire_to_update = Proprietaire.objects.get(id=pk)

    if request.method == 'POST':
        user_form = UserForm(data=request.POST, instance=proprietaire_to_update.user)
        proprietaire_form = ProprietaireForm(data=request.POST, instance=proprietaire_to_update)
        if user_form.is_valid() and proprietaire_form.is_valid():
            user = user_form.save()
            proprietaire = proprietaire_form.save()
            return redirect('detail_proprietaire', pk=pk)

    else:
        user_form = UserForm(instance=proprietaire_to_update.user)
        proprietaire_form = ProprietaireForm(instance=proprietaire_to_update)
    # Render the template depending on the context.
    return render(request, 'admin_interface/proprietaire_form.html', locals())

@login_required
def search_proprietaire(request):
    selected = "proprietaires"
    proprietaires = Proprietaire.objects.all()

    if request.method == 'POST':
        form = ProprietaireSearchForm(request.POST)
        if form.is_valid():

            nom_form = form.cleaned_data['nom']

            if nom_form is not None:
                proprietaires = proprietaires.filter(nom__icontains=nom_form)
    else:
        form = ProprietaireSearchForm()
    return render(request, 'admin_interface/proprietaire_list.html', locals())
