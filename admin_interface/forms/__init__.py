from django.contrib.auth.models import User
from django.forms import DateInput, Form, CharField, PasswordInput, ModelForm


class DateInput(DateInput):
    input_type = "date"

class ConnexionForm(Form):
    username = CharField(label="Nom d'utilisateur", max_length=30)
    password = CharField(label="Mot de passe", widget=PasswordInput)


class UserForm(ModelForm):
    first_name = CharField(required=True, label="Prénom")
    last_name = CharField(required=True, label="Nom")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")