# Generated by Django 4.2.7 on 2024-02-16 23:52

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("taskapp", "0031_remove_task_owner_delete_taskchangerequest"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="notification",
            name="allow_confirm",
        ),
        migrations.RemoveField(
            model_name="notification",
            name="is_archived",
        ),
        migrations.RemoveField(
            model_name="notification",
            name="related_id",
        ),
    ]