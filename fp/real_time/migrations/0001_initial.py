# Generated by Django 4.1.7 on 2023-05-14 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Companies',
            fields=[
                ('symbol', models.CharField(max_length=7, primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'companies',
                'ordering': ['symbol'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='IntradayPrices',
            fields=[
                ('symbol', models.CharField(max_length=7, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField()),
                ('open', models.FloatField(blank=True, null=True)),
                ('high', models.FloatField(blank=True, null=True)),
                ('low', models.FloatField(blank=True, null=True)),
                ('close', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'intraday_prices',
                'ordering': ['timestamp'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Positions',
            fields=[
                ('symbol_id', models.AutoField(primary_key=True, serialize=False)),
                ('symbol', models.CharField(max_length=7)),
                ('side', models.CharField(blank=True, max_length=4, null=True)),
                ('pos_quantity', models.IntegerField(blank=True, null=True)),
                ('average_price', models.FloatField(blank=True, null=True)),
                ('cost', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'positions',
                'ordering': ['symbol'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('transactions_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('symbol', models.CharField(max_length=7)),
                ('timestamp', models.DateTimeField()),
                ('side', models.CharField(blank=True, max_length=4, null=True)),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('execution_id', models.CharField(max_length=50)),
                ('position_quantity', models.IntegerField(blank=True, null=True)),
                ('price', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'transactions',
                'ordering': ['timestamp'],
                'managed': False,
            },
        ),
    ]
