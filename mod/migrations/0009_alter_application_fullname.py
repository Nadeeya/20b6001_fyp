# Generated by Django 4.2.5 on 2024-03-23 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mod', '0008_nonacademicapplication'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='fullname',
            field=models.CharField(default='PENDING', max_length=200),
        ),
    ]