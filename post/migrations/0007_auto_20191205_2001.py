# Generated by Django 2.2.7 on 2019-12-05 16:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0006_auto_20191202_2032'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-id']},
        ),
    ]