# Generated by Django 4.2.7 on 2023-12-28 23:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("taskapp", "0020_taskchangerequest_task_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="taskchangerequest",
            name="change_type",
            field=models.CharField(
                choices=[("OWNER", "owner"), ("ASSIGNED_TO", "assigned")], max_length=20
            ),
        ),
        migrations.CreateModel(
            name="TaskHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("change_type", models.CharField(max_length=50)),
                ("change_date", models.DateTimeField(auto_now_add=True)),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="taskapp.task"
                    ),
                ),
            ],
        ),
    ]
