from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from admin_interface.forms.visites import VisiteSearchForm
from admin_interface.models import EmplacementChoice
from admin_interface.models.animaux import Animal
from admin_interface.models.visite_medicales import VisiteMedicale


class CreateVisite(LoginRequiredMixin, CreateView):
    model = VisiteMedicale
    template_name = "admin_interface/visite_form.html"
    fields = ("date", "type_visite", "montant", "animaux", "commentaire")
    success_url = reverse_lazy("visites")

    def get_form(self, form_class=None):
        form = CreateView.get_form(self, form_class=form_class)
        form.fields["animaux"].queryset = Animal.objects.filter(
            emplacement=EmplacementChoice.REFUGE.name
        ).filter(inactif=False)
        return form


class UpdateVisite(LoginRequiredMixin, UpdateView):
    model = VisiteMedicale
    template_name = "admin_interface/visite_form.html"
    fields = ("date", "type_visite", "montant", "animaux", "commentaire")

    def get_success_url(self):
        return reverse_lazy("detail_visite", kwargs={"pk": self.object.id})

    def get_form(self, form_class=None):
        form = UpdateView.get_form(self, form_class=form_class)
        form.fields["animaux"].queryset = Animal.objects.filter(
            emplacement=EmplacementChoice.REFUGE.name
        ).filter(inactif=False)
        return form


@login_required
def search_visite(request):
    selected = "visites"
    visites = VisiteMedicale.objects.all()

    if request.method == "POST":
        form = VisiteSearchForm(request.POST)
        if form.is_valid():

            date_min_form = form.cleaned_data["date_min"]
            date_max_form = form.cleaned_data["date_max"]

            if date_min_form:
                visites = visites.filter(date__gte=date_min_form)
            if date_max_form:
                visites = visites.filter(date__lte=date_max_form)

    else:
        form = VisiteSearchForm()

    # Pagination : 10 éléments par page
    paginator = Paginator(visites.order_by('-date_mise_a_jour'), 10)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        visites = paginator.page(page)
    except EmptyPage:
        # Si on dépasse la limite de pages, on prend la dernière
        visites = paginator.page(paginator.num_pages())

    return render(request, "admin_interface/visite_list.html", locals())
