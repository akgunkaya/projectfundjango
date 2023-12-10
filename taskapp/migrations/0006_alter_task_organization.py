# Generated by Django 4.2.7 on 2023-12-10 00:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("taskapp", "0005_task_assigned_to_task_organization"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="organization",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="taskapp.organization"
            ),
        ),
    ]