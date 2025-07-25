# Generated by Django 5.2 on 2025-07-17 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Preferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('frequence_recommendation', models.CharField(choices=[('hebdomadaire', 'hedomadaire'), ('mensuel', 'mensuel'), ('Quotidient', 'Quotidient')], default='journaliere', help_text="Frequence d'actulisation de recommendations IA", max_length=40)),
            ],
        ),
    ]
