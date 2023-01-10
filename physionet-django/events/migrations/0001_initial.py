# Generated by Django 3.1.14 on 2023-01-10 21:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.crypto
import django.utils.timezone
import user.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64)),
                ('description', models.TextField(blank=True, null=True)),
                ('category', models.CharField(choices=[('Course', 'Course'), ('Workshop', 'Workshop')], max_length=32)),
                ('added_datetime', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(default=django.utils.timezone.now)),
                ('slug', models.SlugField(default=django.utils.crypto.get_random_string, unique=True)),
                ('allowed_domains', models.CharField(blank=True, max_length=100, null=True, validators=[user.validators.validate_domain_list])),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('view_all_events', 'Can view all events in the console'), ('view_event_menu', 'Can view event menu in the navbar')],
                'unique_together': {('title', 'host')},
            },
        ),
        migrations.CreateModel(
            name='EventParticipant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_datetime', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='events.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'event')},
            },
        ),
    ]
