# Generated by Django 4.2.5 on 2024-03-12 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mod', '0003_alter_bookmarked_application_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='scholarlyInfo',
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='application',
            name='scopusInfo',
            field=models.JSONField(null=True),
        ),
    ]