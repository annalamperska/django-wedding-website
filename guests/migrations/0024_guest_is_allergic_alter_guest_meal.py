# Generated by Django 4.1.7 on 2023-06-19 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guests', '0023_alter_guest_meal'),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='is_allergic',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='guest',
            name='meal',
            field=models.CharField(blank=True, choices=[('all', 'brak'), ('vege', 'vege'), ('vegan', 'vegan')], max_length=20, null=True),
        ),
    ]
