# Generated by Django 4.2.7 on 2025-06-15 11:24

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("calendar_management", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="customevent",
            old_name="note",
            new_name="description",
        ),
    ]
