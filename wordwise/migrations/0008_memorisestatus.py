# Generated by Django 4.2.6 on 2023-11-26 10:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("wordwise", "0007_worddeck_private"),
    ]

    operations = [
        migrations.CreateModel(
            name="MemoriseStatus",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "deck",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="wordwise.worddeck"
                    ),
                ),
                ("memorise", models.ManyToManyField(related_name="memorise", to="wordwise.definition")),
                ("not_memorise", models.ManyToManyField(related_name="not_memorise", to="wordwise.definition")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
