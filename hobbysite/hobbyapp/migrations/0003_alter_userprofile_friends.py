# Generated by Django 5.0.4 on 2024-05-02 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hobbyapp', '0002_alter_userprofile_friends'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='friends',
            field=models.ManyToManyField(blank=True, related_name='friends', to='hobbyapp.userprofile'),
        ),
    ]
