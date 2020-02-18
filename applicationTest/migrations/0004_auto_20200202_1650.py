# Generated by Django 3.0.1 on 2020-02-02 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applicationTest', '0003_animal_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='animal',
            name='category',
        ),
        migrations.AddField(
            model_name='animal',
            name='proprietaire',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='applicationTest.Proprietaire'),
        ),
    ]
