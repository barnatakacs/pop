# Generated by Django 5.1.1 on 2024-09-12 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_picture',
            field=models.ImageField(null=True, upload_to='profile_pictures/'),
        ),
    ]
