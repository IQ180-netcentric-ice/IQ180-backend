# Generated by Django 4.2.5 on 2023-09-14 19:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_alter_detail_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detail',
            name='id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='base.user'),
        ),
    ]
