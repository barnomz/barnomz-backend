# Generated by Django 4.2.7 on 2024-01-13 05:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("barnomz_app", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="professor",
            old_name="first_name",
            new_name="full_name",
        ),
        migrations.RemoveField(
            model_name="classsession",
            name="location",
        ),
        migrations.RemoveField(
            model_name="course",
            name="location",
        ),
        migrations.RemoveField(
            model_name="professor",
            name="last_name",
        ),
        migrations.DeleteModel(
            name="Classroom",
        ),
    ]