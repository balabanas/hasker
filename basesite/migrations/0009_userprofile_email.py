# Generated by Django 4.1.7 on 2023-06-05 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basesite', '0008_alter_answer_author_alter_question_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='email',
            field=models.EmailField(default="defaultemail@localhost", max_length=254, unique=True, null=False),
            preserve_default=False,
        ),
    ]
