# Generated by Django 4.2.7 on 2023-12-09 17:21

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("taskapp", "0002_remove_project_members_remove_project_owner_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
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
                ("title", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("due_date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("TODO", "To Do"),
                            ("IN_PROGRESS", "In Progress"),
                            ("DONE", "Done"),
                        ],
                        default="TODO",
                        max_length=12,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
