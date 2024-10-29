# Generated by Django 5.1.2 on 2024-10-27 12:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter the event category name.', max_length=100)),
                ('description', models.TextField(blank=True, help_text='Brief description of the category.')),
            ],
            options={
                'verbose_name_plural': 'Event Categories',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('level', models.PositiveIntegerField(default=0)),
                ('is_edited', models.BooleanField(default=False)),
                ('path', models.TextField(db_index=True, default='', editable=False)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='events.comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_comments', to='profiles.profile')),
            ],
            options={
                'ordering': ['path'],
            },
        ),
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.profile')),
            ],
            options={
                'unique_together': {('user', 'comment')},
            },
        ),
        migrations.AddField(
            model_name='comment',
            name='likes',
            field=models.ManyToManyField(related_name='liked_comments', through='events.CommentLike', to='profiles.profile'),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Enter the event title.', max_length=200)),
                ('description', models.TextField(help_text='Event description')),
                ('event_type', models.CharField(choices=[('physical', 'Physical Event'), ('text', 'Text-Based Event')], default='physical', max_length=10)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('location', models.CharField(blank=True, help_text='Event location (optional for text-based events).', max_length=200, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='event_images/')),
                ('max_participants', models.PositiveIntegerField(blank=True, help_text='Maximum number of participants.', null=True)),
                ('is_public', models.BooleanField(default=True)),
                ('content', models.TextField(blank=True, help_text='Content for text-based events', null=True)),
                ('attachments', models.FileField(blank=True, help_text='Optional attachments for text-based events', null=True, upload_to='event_attachments/')),
                ('campus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='campus_events', to='profiles.profile')),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.profile')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='events.eventcategory')),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='events.event'),
        ),
        migrations.CreateModel(
            name='EventReaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reaction_type', models.CharField(choices=[('like', '👍'), ('love', '❤️'), ('laugh', '😄'), ('wow', '😮'), ('sad', '😢')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reactions', to='events.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.profile')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('event', 'user', 'reaction_type'), name='unique_event_user_reaction')],
            },
        ),
        migrations.CreateModel(
            name='EventRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('attended', models.BooleanField(default=False)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.profile')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('event', 'participant'), name='unique_event_participant')],
            },
        ),
    ]