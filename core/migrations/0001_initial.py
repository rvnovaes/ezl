# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-15 22:37
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField()),
                ('alter_date', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('street', models.CharField(max_length=255)),
                ('number', models.CharField(max_length=255)),
                ('complement', models.CharField(blank=True, max_length=255)),
                ('city_region', models.CharField(max_length=255)),
                ('zip_code', models.CharField(max_length=255)),
                ('notes', models.TextField(blank=True)),
                ('home_address', models.BooleanField(default=False)),
                ('business_address', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'address',
            },
        ),
        migrations.CreateModel(
            name='AddressType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField()),
                ('alter_date', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='addresstype_alter_user', to=settings.AUTH_USER_MODEL)),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='addresstype_create_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'address_type',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField()),
                ('alter_date', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='city_alter_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'city',
            },
        ),
        migrations.CreateModel(
            name='ContactMechanism',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField()),
                ('alter_date', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('description', models.CharField(max_length=255, unique=True)),
                ('notes', models.CharField(max_length=400)),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='contactmechanism_alter_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'contact_mechanism',
            },
        ),
        migrations.CreateModel(
            name='ContactMechanismType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField()),
                ('alter_date', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='contactmechanismtype_alter_user', to=settings.AUTH_USER_MODEL)),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contactmechanismtype_create_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'contact_mechanism_type',
            },
        ),
        migrations.CreateModel(
            name='ContactUs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('email', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=255)),
                ('message', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'db_table': 'contact_us',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField()),
                ('alter_date', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='country_alter_user', to=settings.AUTH_USER_MODEL)),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='country_create_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'country',
            },
        ),
        migrations.CreateModel(
            name='CourtDistrict',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'db_table': 'court_district',
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField()),
                ('alter_date', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('legal_name', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('is_lawyer', models.BooleanField(default=False)),
                ('is_corresponding', models.BooleanField(default=False)),
                ('legal_type', models.CharField(choices=[('1', 'Jurídica'), ('0', 'Física')], max_length=1)),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='person_alter_user', to=settings.AUTH_USER_MODEL)),
                ('auth_user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='person_create_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'person',
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField()),
                ('alter_date', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('initials', models.CharField(max_length=10, unique=True)),
                ('alter_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='state_alter_user', to=settings.AUTH_USER_MODEL)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Country')),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='state_create_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'state',
            },
        ),
        migrations.AddField(
            model_name='contactmechanism',
            name='contact_mechanism_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.ContactMechanismType'),
        ),
        migrations.AddField(
            model_name='contactmechanism',
            name='create_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contactmechanism_create_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contactmechanism',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Person'),
        ),
        migrations.AddField(
            model_name='city',
            name='court_district',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.CourtDistrict'),
        ),
        migrations.AddField(
            model_name='city',
            name='create_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='city_create_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='city',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.State'),
        ),
        migrations.AddField(
            model_name='address',
            name='address_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.AddressType'),
        ),
        migrations.AddField(
            model_name='address',
            name='alter_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='address_alter_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='address',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.City'),
        ),
        migrations.AddField(
            model_name='address',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Country'),
        ),
        migrations.AddField(
            model_name='address',
            name='create_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='address_create_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='address',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Person'),
        ),
        migrations.AddField(
            model_name='address',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.State'),
        ),
    ]
