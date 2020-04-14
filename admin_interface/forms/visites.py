from django.forms import Form, DateField

from admin_interface.forms import DateInput


class VisiteSearchForm(Form):
    date_min = DateField(
        label="Date de la visite médicale entre le", required=False, widget=DateInput()
    )
    date_max = DateField(label=" et le ", required=False, widget=DateInput())
