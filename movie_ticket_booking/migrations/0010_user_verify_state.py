# Generated by Django 5.1.1 on 2024-10-22 04:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("movie_ticket_booking", "0009_user_verify_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="verify_state",
            field=models.BooleanField(default=False),
        ),
    ]
