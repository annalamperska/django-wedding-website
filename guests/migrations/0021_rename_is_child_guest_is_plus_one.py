# Generated by Django 4.1.7 on 2023-06-18 02:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('guests', '0020_remove_party_is_invited_remove_party_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='guest',
            old_name='is_child',
            new_name='is_plus_one',
        ),
    ]