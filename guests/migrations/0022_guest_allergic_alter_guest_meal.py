# Generated by Django 4.1.7 on 2023-06-18 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guests', '0021_rename_is_child_guest_is_plus_one'),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='allergic',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='guest',
            name='meal',
            field=models.CharField(blank=True, choices=[('all', 'brak'), ('vege', 'vege'), ('vegan', 'vegan'), ('allergic', 'alergia na...')], max_length=20, null=True),
        ),
    ]
