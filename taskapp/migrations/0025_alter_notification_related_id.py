# Generated by Django 4.2.7 on 2024-02-05 18:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("taskapp", "0024_notification_related_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="related_id",
            field=models.IntegerField(null=True),
        ),
    ]
