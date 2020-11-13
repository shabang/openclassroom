from dal import autocomplete

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from admin_interface.forms import UserForm
from admin_interface.forms.proprietaires import ProprietaireForm, ProprietaireSearchForm, AvoirForm
from admin_interface.models.proprietaires import Proprietaire, Avoir


@login_required
def create_proprietaire(request):
    formulaire_valide = False
    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        proprietaire_form = ProprietaireForm(data=request.POST)
        if user_form.is_valid() and proprietaire_form.is_valid():
            # A l'enregistreent de l'utilisateur, identifiant et mot de passe sont autaumatiquement calculés
            user = user_form.save()

            proprietaire = proprietaire_form.save(commit=False)
            proprietaire.user = user
            proprietaire.save()

            formulaire_valide = True
            return redirect("detail_proprietaire", pk=proprietaire.id)

    else:
        user_form = UserForm()
        proprietaire_form = ProprietaireForm()
    # Render the template depending on the context.
    return render(request, "admin_interface/proprietaire_form.html", locals())


@login_required
def update_proprietaire(request, pk):
    proprietaire_to_update = Proprietaire.objects.get(id=pk)

    if request.method == "POST":
        user_form = UserForm(data=request.POST, instance=proprietaire_to_update.user)
        proprietaire_form = ProprietaireForm(
            data=request.POST, instance=proprietaire_to_update
        )
        if user_form.is_valid() and proprietaire_form.is_valid():
            user = user_form.save()
            proprietaire = proprietaire_form.save()
            return redirect("detail_proprietaire", pk=pk)

    else:
        user_form = UserForm(instance=proprietaire_to_update.user)
        proprietaire_form = ProprietaireForm(instance=proprietaire_to_update)
    # Render the template depending on the context.
    return render(request, "admin_interface/proprietaire_form.html", locals())


@login_required
def search_proprietaire(request):
    selected = "proprietaires"
    proprietaire_list = Proprietaire.objects.all().filter(inactif=False)

    if request.method == "POST":
        form = ProprietaireSearchForm(request.POST)
        if form.is_valid():

            nom_form = form.cleaned_data["nom"]
            if nom_form is not None:
                proprietaire_list = proprietaire_list.filter(user__last_name__icontains=nom_form)
    else:
        form = ProprietaireSearchForm()
    # Pagination : 10 éléments par page
    paginator = Paginator(proprietaire_list.order_by('-date_mise_a_jour'), 10)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        proprietaires = paginator.page(page)
    except EmptyPage:
        # Si on dépasse la limite de pages, on prend la dernière
        proprietaires = paginator.page(paginator.num_pages())
    return render(request, "admin_interface/proprietaire_list.html", locals())

class ProprietaireAutocomplete (autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Proprietaire.objects.none()

        qs = Proprietaire.objects.all()

        if self.q:
            qs = qs.filter(user__last_name__istartswith=self.q)

        return qs

class CreateAvoir(LoginRequiredMixin, CreateView):
    model = Avoir
    template_name = "admin_interface/avoir_form.html"
    form_class = AvoirForm
    id_proprietaire = 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proprietaire_id'] = self.request.GET.get("proprietaire", "")
        return context

    def get_form(self, form_class=None):
        form = CreateView.get_form(self, form_class=form_class)
        self.id_proprietaire = self.request.GET.get("proprietaire", "")

        proprietaire = Proprietaire.objects.get(id=self.id_proprietaire)
        form.fields["proprietaire"].initial = proprietaire

        return form

    def get_success_url(self):
        return reverse_lazy("detail_proprietaire", kwargs={"pk": self.id_proprietaire})

@login_required
def utiliser_avoir(request, avoir_id):
    avoir = Avoir.objects.get(id=avoir_id)
    avoir.utiliser()
    avoir.save()
    return redirect("detail_proprietaire", pk=avoir.proprietaire.id)