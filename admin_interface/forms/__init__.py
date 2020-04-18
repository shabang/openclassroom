from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import DateInput, Form, CharField, PasswordInput, ModelForm
from django.utils.text import slugify


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

    def clean(self):
        cleaned_data = ModelForm.clean(self)
        if not self.instance.id:
            # Vérification username unique lors de la création
            first_name = cleaned_data.get("first_name")
            last_name = cleaned_data.get("last_name")
            username = slugify(last_name) + "." + slugify(first_name)
            if User.objects.filter(username=username).exists():
                msg = "Un propriétaire avec ce nom et ce prénom existe déjà, vous ne pouvez pas en créer un nouveau."
                self._errors["first_name"] = self.error_class([msg])
                del cleaned_data["first_name"]
        return cleaned_data