# Generated by Django 5.1.1 on 2024-10-15 08:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("movie_ticket_booking", "0006_favorite"),
    ]

    operations = [
        migrations.CreateModel(
            name="Theater",
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
                ("name", models.CharField(max_length=40)),
                ("place", models.CharField(max_length=40)),
            ],
            options={
                "db_table": "db_theater",
            },
        ),
    ]
