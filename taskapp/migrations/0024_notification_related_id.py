# Generated by Django 4.2.7 on 2024-02-05 17:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("taskapp", "0023_rename_notifications_notification"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="related_id",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]