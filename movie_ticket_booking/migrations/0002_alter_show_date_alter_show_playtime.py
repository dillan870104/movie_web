# Generated by Django 5.1.1 on 2024-10-08 08:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("movie_ticket_booking", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="show",
            name="date",
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name="show",
            name="playTime",
            field=models.DateTimeField(),
        ),
    ]
