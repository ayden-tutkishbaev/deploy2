# Generated by Django 5.0.1 on 2024-04-03 18:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_remove_likes_created_at_remove_likes_post_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='likes',
            new_name='nudges',
        ),
        migrations.DeleteModel(
            name='Likes',
        ),
    ]
