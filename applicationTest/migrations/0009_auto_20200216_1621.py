# Generated by Django 3.0.1 on 2020-02-16 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applicationTest', '0008_remove_adoption_proprietaire'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animal',
            name='adoption',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, to='applicationTest.Adoption'),
        ),
    ]
