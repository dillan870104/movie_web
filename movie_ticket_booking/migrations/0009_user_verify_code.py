# Generated by Django 5.1.1 on 2024-10-22 04:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("movie_ticket_booking", "0008_alter_show_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="verify_code",
            field=models.CharField(default=None, max_length=6),
        ),
    ]
