# Generated by Django 4.2.7 on 2023-12-19 21:10

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("taskapp", "0012_organizationmember"),
    ]

    operations = [
        migrations.RenameField(
            model_name="organizationmember",
            old_name="is_admin",
            new_name="is_owner",
        ),
    ]
